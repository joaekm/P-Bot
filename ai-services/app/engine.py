"""
Adda Search Engine v5.24 - Main Orchestrator

Pipeline:
    IntentAnalyzer → ContextBuilder → Planner → AvropsContainerManager → Synthesizer
         ↓               ↓              ↓                ↓                   ↓
       intent          context         plan         updated_avrop        response

v5.24 Changes:
- All components now use pure dicts (no Pydantic models)
- AvropsContainerManager handles entity changes (deterministic)
- Planner extracts entities, Synthesizer only generates response
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
    AvropsContainerManager,
    SynthesizerComponent
)

# --- CONFIG LOADER ---
def load_config():
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
        'taxonomy': base_dir / paths.get('taxonomy', 'storage/index/adda_taxonomy.json')
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
    Main orchestrator for the Adda Search Engine v5.24.
    
    Pipeline:
    1. IntentAnalyzer - Query → intent dict
    2. ContextBuilder - intent → context dict with documents
    3. Planner - intent + context + avrop → plan dict with entity_changes
    4. AvropsContainerManager - avrop + entity_changes → updated_avrop dict
    5. Synthesizer - plan + updated_avrop → response dict
    """
    
    def __init__(self):
        self.prompts = self._load_prompts()
        self.client = genai.Client(api_key=API_KEY)
        
        # Init ChromaDB (Vector)
        try:
            self.chroma_client = chromadb.PersistentClient(path=str(PATHS['chroma']))
            self.embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
                model_name=CONFIG['ai_engine']['models']['embeddings']
            )
            self.collection = self.chroma_client.get_collection(
                name="adda_knowledge",
                embedding_function=self.embedding_fn
            )
            logger.info(f"✅ ChromaDB OK ({self.collection.count()} dokument)")
        except Exception as e:
            logger.error(f"ChromaDB Init Failed: {e}")
            self.collection = None
            
        # Init Kuzu (Graph)
        self.conn = None
        try:
            kuzu_path = PATHS['kuzu']
            lock_file = kuzu_path / ".lock"
            
            if lock_file.exists():
                logger.error(f"❌ KRITISKT: Kuzu är LÅST. Ta bort: {lock_file}")
                raise RuntimeError(f"Kuzu Graph är låst. Ta bort {lock_file}")
            
            self.db = kuzu.Database(str(kuzu_path))
            self.conn = kuzu.Connection(self.db)
            logger.info("✅ Kuzu OK")
        except Exception as e:
            logger.error(f"Kuzu Init Failed: {e}")

        # Models
        model_lite = CONFIG['ai_engine']['models']['model_lite']
        model_pro = CONFIG['ai_engine']['models']['model_pro']
        
        # Initialize Components
        self.intent_analyzer = IntentAnalyzerComponent(self.client, model_lite, self.prompts)
        self.context_builder = ContextBuilderComponent(PATHS['lake'], self.collection, self.conn)
        self.planner = PlannerComponent(self.client, model_pro, self.prompts)
        self.avrop_container = AvropsContainerManager(PATHS.get('taxonomy'))
        self.synthesizer = SynthesizerComponent(self.client, model_pro, self.prompts)
        
        logger.info("AddaSearchEngine v5.24 initialized")

    def cleanup(self):
        """Stäng Kuzu-anslutning och frigör resurser."""
        if self.conn:
            try:
                del self.conn
                del self.db
                logger.info("✅ Kuzu closed")
            except Exception as e:
                logger.warning(f"Kuzu cleanup warning: {e}")

    def _load_prompts(self):
        try:
            with open(PATHS['prompts'], 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except Exception:
            return {}

    def run(
        self, 
        query: str, 
        history: List[Dict] = None,
        session_state: Dict = None,
        avrop_data: Dict = None
    ) -> Dict[str, Any]:
        """
        Main Pipeline: Intent → Context → Plan → AvropsContainer → Synthesize
        
        Args:
            query: User's current query
            history: Conversation history
            session_state: Legacy session state (for backward compat)
            avrop_data: Current avrop dict (shopping cart)
            
        Returns:
            Dict with response, avrop_data, ui_directives
        """
        history = history or []
        logger.info(f"Query: {query}")
        
        # =====================================================================
        # STEP 1: INTENT ANALYSIS
        # =====================================================================
        intent = self.intent_analyzer.analyze(query, history)
        logger.info(f"Intent: branches={intent.get('branches')}, terms={intent.get('search_terms', [])[:3]}")
        
        # =====================================================================
        # STEP 2: LOAD CURRENT AVROP
        # =====================================================================
        current_step = (session_state or {}).get('current_step', 'step_1_intake')
        
        if avrop_data is None:
            avrop = self._session_state_to_avrop(session_state)
        else:
            avrop = avrop_data if isinstance(avrop_data, dict) else avrop_data
        
        logger.info(f"Avrop: {len(avrop.get('resources', []))} resources, step={current_step}")
        
        # =====================================================================
        # STEP 3: CONTEXT BUILD
        # =====================================================================
        context = self.context_builder.build_context(intent)
        docs = context.get('documents', [])
        logger.info(f"Context: {len(docs)} documents")
        
        # Handle no context
        if not docs:
            return self._handle_no_context(query, avrop, current_step)
        
        # =====================================================================
        # STEP 4: REASONING (Plan) + Entity Extraction
        # =====================================================================
        plan = self.planner.create_plan(
            intent=intent,
            context=context,
            avrop=avrop,
            history=history,
            current_step=current_step
        )
        
        logger.info(f"Plan: tone={plan.get('tone_instruction')}, step={plan.get('target_step')}, "
                   f"entities={len(plan.get('entity_changes', []))}")
        
        # =====================================================================
        # STEP 5: APPLY ENTITY CHANGES (Deterministic)
        # =====================================================================
        entity_changes = plan.get('entity_changes', [])
        updated_avrop = self.avrop_container.apply(avrop, entity_changes)
        
        # Calculate progress
        progress = self.avrop_container.calculate_progress(updated_avrop)
        
        # =====================================================================
        # STEP 6: SYNTHESIS (Generate Response)
        # =====================================================================
        synth_result = self.synthesizer.generate_response(
            query=query,
            plan=plan,
            context=context,
            avrop=updated_avrop,
            history=history
        )
        
        answer = synth_result.get('response', '')
        logger.info(f"Response: {len(answer)} chars")
        
        # =====================================================================
        # STEP 7: BUILD RESPONSE
        # =====================================================================
        target_step = plan.get('target_step', current_step)
        
        # Build session state for backward compatibility
        current_state = {
            "extracted_entities": self._avrop_to_entities(updated_avrop),
            "missing_info": progress.get('missing_fields', []),
            "current_step": target_step,
        }
        
        # Build UI directives
        ui_directives = {
            "taxonomy_branches": intent.get('branches', []),
            "search_terms": intent.get('search_terms', []),
            "target_step": target_step,
            "tone": plan.get('tone_instruction', 'Helpful/Guiding'),
            "completion_percent": progress.get('completion_percent', 0),
            "is_complete": progress.get('is_complete', False),
            "missing_info": progress.get('missing_fields', []),
            "resource_count": len(updated_avrop.get('resources', [])),
        }
        
        # Log trace
        self._log_trace(query, intent, plan, updated_avrop, answer)
        
        return {
            "response": answer,
            "sources": plan.get('primary_sources', []),
            "reasoning": {
                "conclusion": plan.get('primary_conclusion', ''),
                "policy": plan.get('policy_check', ''),
                "tone": plan.get('tone_instruction', ''),
                "target_step": target_step,
                "strategic_input": plan.get('strategic_input', '')
            },
            "avrop_data": updated_avrop,
            "avrop_progress": progress,
            "current_state": current_state,
            "ui_directives": ui_directives
        }
    
    def _session_state_to_avrop(self, session_state: Optional[Dict]) -> Dict:
        """Convert legacy session_state to avrop dict."""
        if not session_state:
            return self.avrop_container.create_empty_avrop()
        
        entities = session_state.get('extracted_entities', {})
        
        avrop = self.avrop_container.create_empty_avrop()
        avrop['location_text'] = entities.get('location')
        avrop['region'] = entities.get('region')
        avrop['volume'] = entities.get('volume')
        avrop['start_date'] = entities.get('start_date')
        avrop['end_date'] = entities.get('end_date')
        avrop['takpris'] = entities.get('price_cap')
        
        # Convert resources
        for old_res in entities.get('resources', []):
            avrop['resources'].append({
                'id': old_res.get('id', ''),
                'roll': old_res.get('role', 'Okänd'),
                'level': old_res.get('level'),
                'antal': old_res.get('quantity', 1),
                'is_complete': bool(old_res.get('level'))
            })
        
        return avrop
    
    def _avrop_to_entities(self, avrop: Dict) -> Dict:
        """Convert avrop dict to legacy entities format."""
        resources = []
        for res in avrop.get('resources', []):
            resources.append({
                "id": res.get('id', ''),
                "role": res.get('roll', 'Okänd'),
                "level": res.get('level'),
                "quantity": res.get('antal', 1),
                "status": "DONE" if res.get('is_complete') else "PENDING",
            })
        
        return {
            "resources": resources,
            "location": avrop.get('location_text'),
            "region": avrop.get('region'),
            "volume": avrop.get('volume'),
            "start_date": avrop.get('start_date'),
            "end_date": avrop.get('end_date'),
            "price_cap": avrop.get('takpris'),
        }
    
    def _handle_no_context(self, query: str, avrop: Dict, current_step: str) -> Dict[str, Any]:
        """Handle case when no context is found."""
        progress = self.avrop_container.calculate_progress(avrop)
        
        return {
            "response": "Jag hittar ingen information om detta. Kan du förtydliga din fråga?",
            "sources": [],
            "reasoning": {"conclusion": "No context found", "tone": "Helpful/Guiding"},
            "avrop_data": avrop,
            "avrop_progress": progress,
            "current_state": {
                "extracted_entities": self._avrop_to_entities(avrop),
                "missing_info": progress.get('missing_fields', []),
                "current_step": current_step,
            },
            "ui_directives": {
                "completion_percent": progress.get('completion_percent', 0),
                "is_complete": False,
                "missing_info": progress.get('missing_fields', []),
            }
        }
    
    def _log_trace(self, query: str, intent: Dict, plan: Dict, avrop: Dict, answer: str):
        """Log pipeline execution for analysis."""
        try:
            trace_entry = {
                "timestamp": datetime.datetime.now().isoformat(),
                "query": query,
                "intent": {
                    "branches": intent.get('branches', []),
                    "search_terms": intent.get('search_terms', []),
                },
                "plan": {
                    "tone": plan.get('tone_instruction', ''),
                    "step": plan.get('target_step', ''),
                    "entity_changes": len(plan.get('entity_changes', [])),
                },
                "avrop": {
                    "resources": len(avrop.get('resources', [])),
                },
                "output": {
                    "response_length": len(answer),
                }
            }

            log_dir = PATHS['logs'].parent
            log_filename = f"session_trace_{datetime.date.today()}.jsonl"
            log_path = log_dir / log_filename
            
            log_dir.mkdir(parents=True, exist_ok=True)

            with open(log_path, 'a', encoding='utf-8') as log_file:
                log_file.write(json.dumps(trace_entry, ensure_ascii=False) + "\n")
                
        except Exception as log_error:
            logger.error(f"Failed to write trace: {log_error}")


# Note: Do NOT create singleton here - main.py handles instantiation
