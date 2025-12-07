"""
Adda Search Engine v5.5 - Main Orchestrator
Coordinates the pipeline: IntentAnalyzer -> ContextBuilder -> Planner -> Synthesizer

v5.5 Changes:
- IntentAnalyzer is now LLM-driven with search_strategy and search_terms
- Entity extraction moved to Synthesizer (no more hardcoded patterns)
- Synthesizer returns SynthesizerResult with response + avrop_changes
- Clean separation: Intent decides WHERE to search, Synthesizer extracts entities

v5.4 Changes:
- Removed ExtractorComponent - entity extraction absorbed into IntentAnalyzer
- Uses new AvropsData model with DELETE support
- RequiredFields-based validation replaces LLM-generated missing_info
- AvropsProgress calculates completion percentage
"""
import os
import json
import logging
import yaml
import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional

import chromadb
from chromadb.utils import embedding_functions
import kuzu
from google import genai
from dotenv import load_dotenv

from .components import (
    IntentAnalyzerComponent,
    ContextBuilderComponent,
    PlannerComponent, 
    SynthesizerComponent
)
from .models import (
    ReasoningPlan,
    AvropsData,
    AvropsProgress,
    Resurs,
)

# --- CONFIG LOADER ---
def load_config():
    # When in app/, go up one level to find config/
    base_dir = Path(__file__).resolve().parent.parent
    config_path = base_dir / "config" / "adda_config.yaml"
    
    if not config_path.exists():
        return None, {}
        
    with open(config_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
        
    paths = config['paths']
    resolved_paths = {
        'lake': base_dir / paths['lake'],
        'chroma': base_dir / paths['chroma_db'],
        'kuzu': base_dir / paths['kuzu_db'],
        'prompts': base_dir / paths['prompts_chat'],
        'logs': base_dir / paths['logs'],
        'session_logs': base_dir / paths.get('session_logs', 'logs')
    }
    return config, resolved_paths

CONFIG, PATHS = load_config()

# Setup Logging
log_dir = PATHS['logs'].parent
log_dir.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - ENGINE - %(levelname)s - %(message)s',
    handlers=[logging.FileHandler(PATHS['logs']), logging.StreamHandler()]
)
logger = logging.getLogger("ADDA_ENGINE")

load_dotenv()
API_KEY = os.getenv("GOOGLE_API_KEY")


class AddaSearchEngine:
    """
    Main orchestrator for the Adda Search Engine v5.5.
    
    Pipeline:
    1. IntentAnalyzer - Query -> IntentTarget (search strategy, no entities)
    2. ContextBuilder - IntentTarget -> Context (dual retrieval)
    3. Planner - Intent + Context -> ReasoningPlan (logic layer)
    4. Synthesizer - Plan + Context + Avrop -> Response + Entity Changes
    
    v5.5: Entity extraction moved to Synthesizer for context-aware extraction.
    """
    
    def __init__(self):
        self.prompts = self._load_prompts()
        self.client = genai.Client(api_key=API_KEY)
        
        # 1. Init Chroma (Vector)
        try:
            self.chroma_client = chromadb.PersistentClient(path=str(PATHS['chroma']))
            self.embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
                model_name=CONFIG['ai_engine']['models']['embeddings']
            )
            self.collection = self.chroma_client.get_collection(
                name="adda_knowledge",
                embedding_function=self.embedding_fn
            )
        except Exception as e:
            logger.error(f"Chroma Init Failed: {e}")
            self.collection = None
            
        # 2. Init Kuzu (Graph)
        self.conn = None
        try:
            self.db = kuzu.Database(str(PATHS['kuzu']))
            self.conn = kuzu.Connection(self.db)
        except Exception as e:
            logger.error(f"Kuzu Init Failed: {e}")

        # Models
        model_lite = CONFIG['ai_engine']['models']['model_lite']
        model_pro = CONFIG['ai_engine']['models']['model_pro']
        model_fast = CONFIG['ai_engine']['models']['model_fast']
        
        # Initialize Components
        self.intent_analyzer = IntentAnalyzerComponent(self.client, model_lite, self.prompts)
        self.context_builder = ContextBuilderComponent(PATHS['lake'], self.collection, self.conn)
        self.planner = PlannerComponent(self.client, model_lite, self.prompts)
        # v5.7: Pass context_builder to Synthesizer for graph lookups (geo, alias)
        self.synthesizer = SynthesizerComponent(self.client, model_fast, self.prompts, self.context_builder)
        
        # Legacy alias for backward compatibility
        self.hunter = self.context_builder
        
        logger.info("AddaSearchEngine v5.7 initialized (Graph-based geo & alias resolution)")

    def _load_prompts(self):
        try:
            with open(PATHS['prompts'], 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except Exception:
            return {}

    def run(
        self, 
        query: str, 
        history: List[Dict] = [], 
        session_state: Dict = None,
        avrop_data: Optional[AvropsData] = None
    ) -> Dict[str, Any]:
        """
        Main Pipeline: Intent -> Context -> Plan -> Synthesize (with entity extraction)
        
        Args:
            query: User's current query
            history: Conversation history
            session_state: Legacy session state from frontend (deprecated, use avrop_data)
            avrop_data: Current AvropsData (shopping cart) from frontend
            
        Returns:
            Dict with response, sources, reasoning, avrop_data, ui_directives
        """
        logger.info(f"New Query: {query}")
        
        # =====================================================================
        # STEP 1: INTENT ANALYSIS (LLM-driven search strategy)
        # v5.5: No entity extraction here - just search strategy
        # =====================================================================
        intent_target = self.intent_analyzer.analyze(query, history)
        logger.info(f"Intent: {intent_target.intent_category}, "
                   f"branches={[b.value for b in intent_target.taxonomy_branches]}, "
                   f"search_terms={intent_target.search_terms[:3]}, "
                   f"strategy={intent_target.search_strategy}")
        
        # =====================================================================
        # STEP 2: LOAD CURRENT AVROP (from frontend or legacy state)
        # v5.8: Also extract previous step for step progression control
        # v5.9: Ensure new sessions ALWAYS start at step_1_intake
        # =====================================================================
        if session_state and 'current_step' in session_state:
            previous_step = session_state['current_step']
        else:
            previous_step = 'step_1_intake'  # New sessions always start here
        
        if avrop_data is None:
            current_avrop = self._session_state_to_avrop(session_state)
        else:
            current_avrop = avrop_data
        
        logger.info(f"Current Avrop: {len(current_avrop.resources)} resources, step={previous_step}")
        
        # =====================================================================
        # STEP 3: CONTEXT BUILD (Retrieve using search_strategy)
        # v5.7: Now returns ContextResult with documents AND resolved relations
        # =====================================================================
        if intent_target.should_block_secondary():
            logger.info("🛡️ GHOST MODE: Blocking SECONDARY files")
        
        context = self.context_builder.build_context(intent_target)
        
        # Check if this is a "cart operation" (no search strategy enabled)
        is_cart_operation = not any([
            intent_target.should_search_lake(),
            intent_target.should_search_vector(),
            intent_target.should_search_graph()
        ])
        
        # v5.7: Check documents OR graph knowledge
        has_context = bool(context.documents) or context.has_graph_knowledge()
        
        if not has_context and not is_cart_operation:
            # No context found and this was a real search - return error
            progress = AvropsProgress.calculate(current_avrop)
            current_state = self._avrop_to_session_state(current_avrop, progress, intent_target, previous_step)
            return self._handle_no_context(query, intent_target, current_state, current_avrop, progress)
        
        if is_cart_operation:
            logger.info("Cart operation detected - proceeding without context")
        
        # Track hits for logging (v5.7: use context.documents)
        lake_hits = {k: v for k, v in context.documents.items() if v.get('source') == 'TOPIC_MATCH'}
        vector_hits = {k: v for k, v in context.documents.items() if 'VECTOR' in v.get('source', '')}
        graph_hits = {k: v for k, v in context.documents.items() if v.get('source') == 'GRAPH'}
        
        logger.info(f"Context: {len(lake_hits)} lake, {len(vector_hits)} vector, {len(graph_hits)} graph")
        
        # v5.7: Log resolved graph relations
        if context.has_graph_knowledge():
            logger.info(f"🧠 Graph knowledge: {len(context.resolved_locations)} locations, "
                       f"{len(context.resolved_roles)} roles, {len(context.resolved_aliases)} aliases")
        
        # =====================================================================
        # STEP 4: REASONING (Plan) - includes validation
        # v5.8: Pass current_step to prevent backward jumps
        # v5.9: Pass history so Planner understands confirmations
        # =====================================================================
        reasoning_plan = self.planner.create_plan(intent_target, context, current_step=previous_step, history=history)
        
        logger.info(f"Plan: tone={reasoning_plan.tone_instruction}, "
                   f"step={reasoning_plan.target_step}, "
                   f"warning={reasoning_plan.requires_warning()}")
        
        # =====================================================================
        # STEP 5: SYNTHESIS (Generate Response + Extract Entities)
        # v5.5: Synthesizer now handles entity extraction
        # =====================================================================
        synth_result = self.synthesizer.generate_response(
            query=query,
            plan=reasoning_plan,
            context=context,
            current_avrop=current_avrop,
            history=history
        )
        
        # Get updated avrop from Synthesizer
        updated_avrop = synth_result.updated_avrop or current_avrop
        answer = synth_result.response
        
        logger.info(f"Synthesizer: {len(synth_result.avrop_changes)} entity changes, "
                   f"{len(updated_avrop.resources)} resources")
        
        # Calculate progress using RequiredFields
        progress = AvropsProgress.calculate(updated_avrop)
        
        # Build current_state for backward compatibility
        # v5.8: Include current_step from reasoning_plan for next turn
        current_state = self._avrop_to_session_state(
            updated_avrop, progress, intent_target, reasoning_plan.target_step
        )
        
        # Handle forced strategy from Planner
        if reasoning_plan.forced_strategy:
            current_state["forced_strategy"] = reasoning_plan.forced_strategy
            logger.info(f"📋 Strategy forced to {reasoning_plan.forced_strategy} by Planner")
        
        # Note: validation_warnings and data_validation are internal info for Synthesizer
        # They are included in the reasoning injection so Synthesizer can adjust tone/content
        # We do NOT prefix the user-facing response with these - that was confusing users
        
        # Only show constraint_violations if they are actual blocking issues
        # (e.g., "Volym överstiger max tillåtet för DR") - but even these should be
        # handled naturally by Synthesizer in its response, not as ugly prefixes
        
        # =====================================================================
        # STEP 6: BUILD RESPONSE
        # =====================================================================
        sources = reasoning_plan.get_all_sources()
        
        # Build UI directives
        ui_directives = self._build_ui_directives(
            intent_target, reasoning_plan, current_state, updated_avrop, progress
        )
        
        # Log trace
        self._log_trace(
            query=query,
            intent_target=intent_target,
            context=context,
            reasoning_plan=reasoning_plan,
            current_state=current_state,
            answer=answer,
            entity_changes=len(synth_result.avrop_changes)
        )
        
        return {
            "response": answer,
            "sources": sources,
            "reasoning": {
                "conclusion": reasoning_plan.primary_conclusion,
                "policy": reasoning_plan.policy_check,
                "tone": reasoning_plan.tone_instruction,
                "conflicts": reasoning_plan.conflict_resolution,
                "validation": reasoning_plan.data_validation,
                "validation_warnings": reasoning_plan.validation_warnings,
                "forced_strategy": reasoning_plan.forced_strategy,
                "target_step": reasoning_plan.target_step
            },
            # v5.5: Return avrop_data from Synthesizer
            "avrop_data": updated_avrop.model_dump(),
            "avrop_progress": progress.model_dump(),
            "current_state": current_state,  # Legacy, for backward compatibility
            "ui_directives": ui_directives
        }
    
    def _session_state_to_avrop(self, session_state: Optional[Dict]) -> AvropsData:
        """Convert legacy session_state to AvropsData."""
        from .models import Region  # Import here to avoid circular
        
        if not session_state:
            return AvropsData()
        
        entities = session_state.get('extracted_entities', {})
        
        # Parse region from session state
        region_value = entities.get('region')
        region = None
        if region_value:
            try:
                region = Region(region_value)
            except ValueError:
                pass
        
        avrop = AvropsData(
            location_text=entities.get('location'),
            region=region,  # v5.8: Restore region from session state
            volume=entities.get('volume'),
            start_date=entities.get('start_date'),
            end_date=entities.get('end_date'),  # v5.8: Restore end_date
            takpris=entities.get('price_cap'),
        )
        
        # Convert legacy resources
        for old_res in entities.get('resources', []):
            resurs = Resurs(
                id=old_res.get('id', ''),
                roll=old_res.get('role', 'Okänd'),
                level=old_res.get('level'),
                antal=old_res.get('quantity', 1),
            )
            avrop.resources.append(resurs)
        
        return avrop
    
    def _avrop_to_session_state(
        self, 
        avrop: AvropsData, 
        progress: AvropsProgress,
        intent_target,
        current_step: str = "step_1_intake"
    ) -> Dict:
        """Convert AvropsData to legacy session_state format."""
        return {
            "extracted_entities": self._avrop_to_legacy_entities(avrop),
            "missing_info": progress.missing_fields,
            "current_intent": intent_target.intent_category,
            "confidence": intent_target.confidence,
            "current_step": current_step,  # v5.8: Track current step for next turn
        }
    
    def _avrop_to_legacy_entities(self, avrop: AvropsData) -> Dict:
        """Convert AvropsData to legacy extracted_entities format."""
        resources = []
        for res in avrop.resources:
            resources.append({
                "id": res.id,
                "role": res.roll,
                "level": res.level,
                "quantity": res.antal,
                "status": "DONE" if res.is_complete else "PENDING",
            })
        
        return {
            "resources": resources,
            "location": avrop.location_text,
            "region": avrop.region.value if avrop.region else None,  # v5.8: Include region enum
            "volume": avrop.volume,
            "start_date": avrop.start_date,
            "end_date": avrop.end_date,  # v5.8: Include end_date
            "price_cap": avrop.takpris,
        }
    
    def _handle_no_context(
        self, 
        query: str, 
        intent_target, 
        current_state: Dict,
        avrop: AvropsData,
        progress: AvropsProgress
    ) -> Dict[str, Any]:
        """Handle case when no context is found."""
        return {
            "response": "Jag hittar ingen information om detta i din valda kontext.",
            "sources": [],
            "reasoning": {
                "conclusion": "No context found",
                "policy": "N/A",
                "tone": "Helpful/Guiding"
            },
            "avrop_data": avrop.model_dump(),
            "avrop_progress": progress.model_dump(),
            "current_state": current_state,
            "ui_directives": self._build_ui_directives(
                intent_target, None, current_state, avrop, progress
            )
        }
    
    def _build_ui_directives(
        self, 
        intent_target, 
        reasoning_plan, 
        current_state: Dict,
        avrop: Optional[AvropsData] = None,
        progress: Optional[AvropsProgress] = None
    ) -> Dict[str, Any]:
        """Build UI directives for frontend."""
        directives = {
            "current_intent": intent_target.intent_category,
            "detected_topics": intent_target.detected_topics,
            "detected_entities": intent_target.detected_entities,
            "taxonomy_branches": [b.value for b in intent_target.taxonomy_branches],
            "search_terms": intent_target.search_terms,  # v5.5: Include search terms
            "entity_summary": current_state.get('extracted_entities', {}),
            "missing_info": current_state.get('missing_info', []),
            "ghost_mode": intent_target.should_block_secondary()
        }
        
        # Add avrop-specific directives
        if avrop:
            directives["avrop_typ"] = avrop.avrop_typ.value if avrop.avrop_typ else None
            directives["resource_count"] = len(avrop.resources)
        
        if progress:
            directives["completion_percent"] = progress.completion_percent
            directives["is_complete"] = progress.is_complete
            directives["constraint_violations"] = progress.constraint_violations
        
        if reasoning_plan:
            directives["target_step"] = reasoning_plan.target_step
            directives["tone"] = reasoning_plan.tone_instruction
            directives["has_warning"] = reasoning_plan.requires_warning()
        
        return directives
    
    def _log_trace(
        self, 
        query: str, 
        intent_target, 
        context: Dict,
        reasoning_plan,
        current_state: Dict,
        answer: str,
        entity_changes: int = 0
    ):
        """Black Box Recorder - Log pipeline execution for analysis."""
        try:
            # Extract document IDs and types for debugging
            doc_summary = [
                {"id": doc_id, "type": doc.get('type'), "authority": doc.get('authority'), "source": doc.get('source')}
                for doc_id, doc in context.documents.items()
            ]
            
            # Extract graph resolutions
            graph_resolutions = {
                "locations": [{"city": loc.city, "county": loc.county, "area": loc.area} 
                             for loc in context.resolved_locations] if context.resolved_locations else [],
                "roles": [{"name": r.role_name, "area": r.kompetensomrade} 
                         for r in context.resolved_roles] if context.resolved_roles else [],
                "aliases": context.resolved_aliases if context.resolved_aliases else {}
            }
            
            trace_entry = {
                "timestamp": datetime.datetime.now().isoformat(),
                "query": query,
                "intent": {
                    "category": intent_target.intent_category,
                    "branches": [b.value for b in intent_target.taxonomy_branches],
                    "search_terms": intent_target.search_terms,
                    "search_strategy": intent_target.search_strategy,
                    "topics": intent_target.detected_topics,
                    "ghost_mode": intent_target.should_block_secondary()
                },
                "context": {
                    "total_docs": len(context.documents),
                    "primary_count": sum(1 for d in context.documents.values() if d.get('authority') == 'PRIMARY'),
                    "secondary_count": sum(1 for d in context.documents.values() if d.get('authority') == 'SECONDARY'),
                    "documents": doc_summary,
                    "graph_resolutions": graph_resolutions
                },
                "reasoning": {
                    "conclusion": reasoning_plan.primary_conclusion if reasoning_plan else "N/A",
                    "policy": reasoning_plan.policy_check if reasoning_plan else "N/A",
                    "tone": reasoning_plan.tone_instruction if reasoning_plan else "N/A",
                    "step": reasoning_plan.target_step if reasoning_plan else "N/A",
                    "warning": reasoning_plan.requires_warning() if reasoning_plan else False
                } if reasoning_plan else {"status": "NO_CONTEXT"},
                "session_state": {
                    "resources": len(current_state.get('extracted_entities', {}).get('resources', [])),
                    "missing_info": current_state.get('missing_info', []),
                    "entity_changes": entity_changes,
                    "extracted_entities": current_state.get('extracted_entities', {}),
                    "avrop": {
                        "region": current_state.get('extracted_entities', {}).get('region'),
                        "start_date": current_state.get('extracted_entities', {}).get('start_date'),
                        "end_date": current_state.get('extracted_entities', {}).get('end_date'),
                        "volume": current_state.get('extracted_entities', {}).get('volume'),
                        "avropsform": current_state.get('extracted_entities', {}).get('avropsform'),
                        "prismodell": current_state.get('extracted_entities', {}).get('prismodell'),
                        "pris_vikt": current_state.get('extracted_entities', {}).get('pris_vikt'),
                        "kvalitet_vikt": current_state.get('extracted_entities', {}).get('kvalitet_vikt'),
                        "location_text": current_state.get('extracted_entities', {}).get('location_text'),
                        "anbudsomrade": current_state.get('extracted_entities', {}).get('anbudsomrade')
                    }
                },
                "output": {
                    "response_length": len(answer),
                    "response_preview": answer[:150] + "..." if len(answer) > 150 else answer
                }
            }

            log_dir = PATHS['session_logs']
            log_filename = f"session_trace_{datetime.date.today()}.jsonl"
            log_path = log_dir / log_filename
            
            log_dir.mkdir(parents=True, exist_ok=True)

            with open(log_path, 'a', encoding='utf-8') as log_file:
                log_file.write(json.dumps(trace_entry, ensure_ascii=False) + "\n")
                
        except Exception as log_error:
            logger.error(f"Failed to write session trace: {log_error}")


# Singleton for import
engine = AddaSearchEngine()
