"""
Adda Search Engine v5.2 - Main Orchestrator
Coordinates the pipeline: IntentAnalyzer -> ContextBuilder -> Planner -> Synthesizer

v5.2 Changes:
- New pipeline flow with Planner (Logic Layer) between Context and Synthesis
- ReasoningPlan model for structured reasoning output
- Removed redundant Extractor step (IntentAnalyzer handles intent)
"""
import os
import json
import logging
import yaml
import datetime
from pathlib import Path
from typing import List, Dict, Any

import chromadb
from chromadb.utils import embedding_functions
import kuzu
from google import genai
from dotenv import load_dotenv

from .components import (
    ExtractorComponent,
    IntentAnalyzerComponent,
    ContextBuilderComponent,
    PlannerComponent, 
    SynthesizerComponent
)
from .models import ReasoningPlan
from .validators import normalize_entities, validate_entities

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
        'logs': base_dir / paths['logs']
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
    Main orchestrator for the Adda Search Engine v5.2.
    
    Pipeline:
    1. IntentAnalyzer - Query -> IntentTarget (taxonomy mapping)
    2. ContextBuilder - IntentTarget -> Context (dual retrieval)
    3. Planner - Intent + Context -> ReasoningPlan (logic layer)
    4. Synthesizer - ReasoningPlan + Context -> Response
    
    Additionally:
    - Extractor for session state (resources, location, etc.)
    - Validator for constraint checking
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
        
        # Initialize Components
        self.extractor = ExtractorComponent(self.client, model_lite, self.prompts)
        self.intent_analyzer = IntentAnalyzerComponent(self.client, model_lite, self.prompts)
        self.context_builder = ContextBuilderComponent(PATHS['lake'], self.collection, self.conn)
        self.planner = PlannerComponent(self.client, model_lite, self.prompts)
        self.synthesizer = SynthesizerComponent(self.client, model_pro, self.prompts)
        
        # Legacy alias for backward compatibility
        self.hunter = self.context_builder
        
        logger.info("AddaSearchEngine v5.2 initialized with Logic Layer (Planner)")

    def _load_prompts(self):
        try:
            with open(PATHS['prompts'], 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except Exception:
            return {}

    def run(self, query: str, history: List[Dict] = [], session_state: Dict = None) -> Dict[str, Any]:
        """
        Main Pipeline: Intent -> Context -> Plan -> Synthesize
        
        Args:
            query: User's current query
            history: Conversation history
            session_state: Existing session state from frontend
            
        Returns:
            Dict with response, sources, reasoning_plan, current_state, ui_directives
        """
        logger.info(f"New Query: {query}")
        
        # =====================================================================
        # STEP 1: INTENT ANALYSIS (Understand)
        # =====================================================================
        intent_target = self.intent_analyzer.analyze(query, history)
        logger.info(f"Intent: {intent_target.intent_category}, "
                   f"branches={[b.value for b in intent_target.taxonomy_branches]}, "
                   f"topics={intent_target.detected_topics}")
        
        # =====================================================================
        # STEP 2: ENTITY EXTRACTION (Session State)
        # =====================================================================
        extracted_delta = self.extractor.extract(query, history)
        current_state = self.extractor.merge(session_state, extracted_delta)
        
        # Sync intent from IntentAnalyzer to state
        current_state['current_intent'] = intent_target.intent_category
        
        extracted_entities = current_state.get('extracted_entities', {})
        
        # Normalize entities
        extracted_entities = normalize_entities(extracted_entities)
        current_state['extracted_entities'] = extracted_entities
        
        logger.info(f"Session State: {len(extracted_entities.get('resources', []))} resources, "
                   f"missing: {current_state.get('missing_info')}")
        
        # =====================================================================
        # STEP 3: VALIDATION (Constraint Check)
        # =====================================================================
        validated_entities, validation_issues = validate_entities(extracted_entities)
        current_state['extracted_entities'] = validated_entities
        
        # Handle BLOCK (abort immediately)
        block_issues = [i for i in validation_issues if i.get("type") == "BLOCK"]
        if block_issues:
            return self._handle_blocked_request(
                query, intent_target, current_state, block_issues, validation_issues
            )
        
        # Handle STRATEGY_FORCE
        strategy_notices = []
        for issue in validation_issues:
            if issue.get("type") == "STRATEGY_FORCE":
                strategy_notices.append(f"⚠️ **Notis:** {issue.get('message')}")
                if issue.get("action") == "TRIGGER_STRATEGY_FKU":
                    current_state["forced_strategy"] = "FKU"
                    logger.info("📋 Strategy forced to FKU by Validator")
        
        # =====================================================================
        # STEP 4: CONTEXT BUILD (Retrieve)
        # =====================================================================
        if intent_target.should_block_secondary():
            logger.info("🛡️ GHOST MODE: Blocking SECONDARY files")
        
        context = self.context_builder.build_context(intent_target)
        
        if not context:
            return self._handle_no_context(query, intent_target, current_state)
        
        # Track hits for logging
        topic_hits = {k: v for k, v in context.items() if v.get('source') == 'TOPIC_MATCH'}
        vector_hits = {k: v for k, v in context.items() if 'VECTOR' in v.get('source', '')}
        graph_hits = {k: v for k, v in context.items() if v.get('source') == 'GRAPH'}
        
        logger.info(f"Context: {len(topic_hits)} topic, {len(vector_hits)} vector, {len(graph_hits)} graph")
        
        # =====================================================================
        # STEP 5: REASONING (Plan)
        # =====================================================================
        reasoning_plan = self.planner.create_plan(intent_target, context)
        
        logger.info(f"Plan: tone={reasoning_plan.tone_instruction}, "
                   f"step={reasoning_plan.target_step}, "
                   f"warning={reasoning_plan.requires_warning()}")
        
        # =====================================================================
        # STEP 6: SYNTHESIS (Generate Response)
        # =====================================================================
        answer = self.synthesizer.generate_response(
            query=query,
            plan=reasoning_plan,
            context=context,
            extracted_entities=extracted_entities
        )
        
        # Inject strategy notices if any
        if strategy_notices:
            prefix = "\n\n".join(strategy_notices) + "\n\n"
            answer = prefix + answer
        
        # =====================================================================
        # STEP 7: BUILD RESPONSE
        # =====================================================================
        sources = reasoning_plan.get_all_sources()
        
        # Build UI directives
        ui_directives = self._build_ui_directives(intent_target, reasoning_plan, current_state)
        
        # Log trace
        self._log_trace(
            query=query,
            intent_target=intent_target,
            context=context,
            reasoning_plan=reasoning_plan,
            current_state=current_state,
            answer=answer
        )
        
        return {
            "response": answer,
            "sources": sources,
            "reasoning": {
                "conclusion": reasoning_plan.primary_conclusion,
                "policy": reasoning_plan.policy_check,
                "tone": reasoning_plan.tone_instruction,
                "conflicts": reasoning_plan.conflict_resolution,
                "validation": reasoning_plan.data_validation
            },
            "current_state": current_state,
            "ui_directives": ui_directives
        }
    
    def _handle_blocked_request(
        self, 
        query: str, 
        intent_target, 
        current_state: Dict,
        block_issues: List[Dict],
        all_issues: List[Dict]
    ) -> Dict[str, Any]:
        """Handle requests blocked by validator."""
        block_msg = block_issues[0].get('message', "Begäran stoppad av regelverk.")
        logger.warning(f"🚫 Request BLOCKED: {block_msg}")
        
        # Log the blocked request
        self._log_trace(
            query=query,
            intent_target=intent_target,
            context={},
            reasoning_plan=None,
            current_state=current_state,
            answer=f"🛑 BLOCKED: {block_msg}"
        )
        
        return {
            "response": f"🛑 **Åtgärd krävs:** {block_msg}",
            "sources": [i.get('source') for i in block_issues if i.get('source')],
            "reasoning": {
                "conclusion": "BLOCKED",
                "policy": "Validator constraint",
                "tone": "Strict/Warning",
                "validation": block_msg
            },
            "current_state": current_state,
            "ui_directives": {
                "current_intent": "FACT",
                "missing_info": [],
                "validation_blocked": True
            }
        }
    
    def _handle_no_context(
        self, 
        query: str, 
        intent_target, 
        current_state: Dict
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
            "current_state": current_state,
            "ui_directives": self._build_ui_directives(intent_target, None, current_state)
        }
    
    def _build_ui_directives(
        self, 
        intent_target, 
        reasoning_plan, 
        current_state: Dict
    ) -> Dict[str, Any]:
        """Build UI directives for frontend."""
        directives = {
            "current_intent": intent_target.intent_category,
            "detected_topics": intent_target.detected_topics,
            "detected_entities": intent_target.detected_entities,
            "taxonomy_branches": [b.value for b in intent_target.taxonomy_branches],
            "entity_summary": current_state.get('extracted_entities', {}),
            "missing_info": current_state.get('missing_info', []),
            "ghost_mode": intent_target.should_block_secondary()
        }
        
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
        answer: str
    ):
        """Black Box Recorder - Log pipeline execution for analysis."""
        try:
            trace_entry = {
                "timestamp": datetime.datetime.now().isoformat(),
                "query": query,
                "intent": {
                    "category": intent_target.intent_category,
                    "branches": [b.value for b in intent_target.taxonomy_branches],
                    "topics": intent_target.detected_topics,
                    "entities": intent_target.detected_entities,
                    "ghost_mode": intent_target.should_block_secondary()
                },
                "context": {
                    "total_docs": len(context),
                    "primary_count": sum(1 for d in context.values() if d.get('authority') == 'PRIMARY'),
                    "secondary_count": sum(1 for d in context.values() if d.get('authority') == 'SECONDARY')
                },
                "reasoning": {
                    "conclusion": reasoning_plan.primary_conclusion if reasoning_plan else "N/A",
                    "policy": reasoning_plan.policy_check if reasoning_plan else "N/A",
                    "tone": reasoning_plan.tone_instruction if reasoning_plan else "N/A",
                    "step": reasoning_plan.target_step if reasoning_plan else "N/A",
                    "warning": reasoning_plan.requires_warning() if reasoning_plan else False
                } if reasoning_plan else {"status": "BLOCKED or NO_CONTEXT"},
                "session_state": {
                    "resources": len(current_state.get('extracted_entities', {}).get('resources', [])),
                    "missing_info": current_state.get('missing_info', [])
                },
                "output": {
                    "response_length": len(answer),
                    "response_preview": answer[:150] + "..." if len(answer) > 150 else answer
                }
            }

            log_dir = PATHS['logs'].parent
            log_filename = f"session_trace_{datetime.date.today()}.jsonl"
            log_path = log_dir / log_filename
            
            log_dir.mkdir(parents=True, exist_ok=True)

            with open(log_path, 'a', encoding='utf-8') as log_file:
                log_file.write(json.dumps(trace_entry, ensure_ascii=False) + "\n")
                
        except Exception as log_error:
            logger.error(f"Failed to write session trace: {log_error}")


# Singleton for import
engine = AddaSearchEngine()
