"""
Adda Search Engine v5 - Main Orchestrator
Coordinates the pipeline: Extractor -> Validator -> Planner -> Hunter -> Synthesizer
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

from .components import ExtractorComponent, PlannerComponent, HunterComponent, SynthesizerComponent
from .validators import normalize_entities

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
    Main orchestrator for the Adda Search Engine v5.
    
    Pipeline:
    0. Extractor - Entity extraction from conversation
    0.5. Validator - Normalize and validate entities
    1. Planner - Analyze query and create search strategy
    2. Hunter - Search Lake (files) and Vector (ChromaDB)
    3. Synthesizer - Generate response with persona
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
            
        # 2. Init Kuzu (Graph) - Placeholder for future advanced queries
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
        self.planner = PlannerComponent(self.client, model_lite, self.prompts)
        self.hunter = HunterComponent(PATHS['lake'], self.collection)
        self.synthesizer = SynthesizerComponent(self.client, model_pro, self.prompts)
        
        logger.info("AddaSearchEngine v5 initialized with modular components")

    def _load_prompts(self):
        try:
            with open(PATHS['prompts'], 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except Exception:
            return {}

    def run(self, query: str, history: List[Dict] = [], session_state: Dict = None) -> Dict[str, Any]:
        """Main Pipeline with State Persistence"""
        logger.info(f"New Query: {query}")
        
        # 0. EXTRACT (Delta from latest message)
        extracted_delta = self.extractor.extract(query, history)
        
        # 0.5 MERGE (Combine with existing state from frontend)
        current_state = self.extractor.merge(session_state, extracted_delta)
        
        current_intent = current_state.get('current_intent', 'INSPIRATION')
        extracted_entities = current_state.get('extracted_entities', {})
        
        # 0.6 VALIDATE & NORMALIZE
        extracted_entities = normalize_entities(extracted_entities)
        current_state['extracted_entities'] = extracted_entities
        
        logger.info(f"Merged State Resources: {len(extracted_entities.get('resources', []))}")
        logger.info(f"Current Intent: {current_intent}, Missing: {current_state.get('missing_info')}")
        
        # KILLSWITCH LOGIC: Determine allowed authority levels based on intent
        if current_intent == "FACT":
            allowed_authorities = ["PRIMARY"]
            logger.info("🛡️ GHOST MODE ACTIVATED: Blocking SECONDARY files based on intent 'FACT'")
        else:
            allowed_authorities = ["PRIMARY", "SECONDARY"]
        
        # 1. PLAN
        plan = self.planner.plan(query, history)
        target_step = plan.get('target_step', 'general')
        target_type = plan.get('target_type', 'DEFINITION')
        
        candidates = {}
        hunter_hits = {}
        
        # 2. HUNT (If looking for rules/instructions) - with authority filter
        if target_type in ['RULE', 'INSTRUCTION', 'DATA_POINTER']:
            hunter_hits = self.hunter.search_lake(target_step, target_type, allowed_authorities)
            candidates.update(hunter_hits)
            
        # 3. VECTOR (Understanding) - with authority filter
        vector_query = plan.get('vector_query', query)
        vector_hits = self.hunter.search_vector(vector_query, target_step, allowed_authorities)
        
        # Merge (Vector fills in where Hunter misses)
        for k, v in vector_hits.items():
            if k not in candidates:
                candidates[k] = v
        
        # 4. CONTEXT PREP
        context_docs = []
        sources = []
        
        # Sort: Rules first!
        sorted_candidates = sorted(
            candidates.values(), 
            key=lambda x: 0 if x['type'] == 'RULE' else 1
        )
        
        for doc in sorted_candidates[:8]:  # Max 8 block context
            authority_tag = f" [{doc.get('authority', 'UNKNOWN')}]" if doc.get('authority') else ""
            context_docs.append(f"--- BLOCK: {doc['type']}{authority_tag} (File: {doc['filename']}) ---\n{doc['content']}")
            sources.append(doc['filename'])
            
        if not context_docs:
            return {
                "response": "Jag hittar ingen information om detta i din valda kontext.", 
                "sources": [], 
                "thoughts": plan,
                "current_state": current_state
            }
            
        # 5. SYNTHESIZE
        answer = self.synthesizer.synthesize(query, context_docs, extracted_entities, target_step)
        
        # --- BLACK BOX RECORDER ---
        self._log_trace(query, current_intent, extracted_entities, current_state, 
                        plan, target_step, target_type, hunter_hits, vector_hits, 
                        sources, answer)

        return {
            "response": answer,
            "sources": list(set(sources)),
            "thoughts": plan,
            "current_state": current_state
        }
    
    def _log_trace(self, query, current_intent, extracted_entities, current_state,
                   plan, target_step, target_type, hunter_hits, vector_hits, sources, answer):
        """Black Box Recorder - Log pipeline execution for analysis."""
        try:
            used_persona = self.synthesizer.get_persona_name(target_step)

            trace_entry = {
                "timestamp": datetime.datetime.now().isoformat(),
                "session_input": {
                    "query": query,
                    "extracted_intent": current_intent,
                    "extracted_entities": extracted_entities,
                    "missing_info": current_state.get('missing_info', [])
                },
                "pipeline_logic": {
                    "step_1_planner": plan,
                    "target_step": target_step,
                    "target_type": target_type,
                    "used_persona": used_persona,
                    "ghost_mode": current_intent == "FACT"
                },
                "search_results": {
                    "hunter_hits": len(hunter_hits),
                    "vector_hits": len(vector_hits),
                    "final_sources": sources
                },
                "output": {
                    "response_length": len(answer),
                    "response_preview": answer[:100] + "..." if answer else ""
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

