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
from google.genai import types
from dotenv import load_dotenv

# --- CONFIG LOADER ---
def load_config():
    base_dir = Path(__file__).parent
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
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - ENGINE - %(levelname)s - %(message)s',
    handlers=[logging.FileHandler(PATHS['logs']), logging.StreamHandler()]
)
logger = logging.getLogger("ADDA_ENGINE")

load_dotenv()
API_KEY = os.getenv("GOOGLE_API_KEY")

class AddaSearchEngine:
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
            
        # 2. Init Kuzu (Graph) - Placeholder för framtida avancerade queries
        try:
            self.db = kuzu.Database(str(PATHS['kuzu']))
            self.conn = kuzu.Connection(self.db)
        except Exception as e:
            logger.error(f"Kuzu Init Failed: {e}")

        # Models
        self.model_planner = CONFIG['ai_engine']['models']['model_lite'] 
        self.model_synthesizer = CONFIG['ai_engine']['models']['model_pro']
        self.model_extractor = CONFIG['ai_engine']['models']['model_lite']  # For entity extraction

    def _load_prompts(self):
        try:
            with open(PATHS['prompts'], 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except Exception:
            return {}

    def _extract_session_state(self, query: str, history: List[Dict]) -> Dict:
        """
        Entity Extraction - Creates a "Shadow State" from conversation history.
        
        Uses gemini-flash-lite to analyze the conversation and extract:
        - extracted_entities: structured data about the procurement
        - missing_info: list of what's still needed
        - current_intent: FACT (rules/regler) or INSPIRATION (help/examples)
        
        This runs BEFORE the Planner to give context about what we know so far.
        """
        # Load prompt from YAML
        raw_prompt = self.prompts.get('extractor', {}).get('instruction', '')
        
        if not raw_prompt:
            logger.warning("Extractor prompt not found in assistant_prompts.yaml")
            return self._fallback_session_state()
        
        # Format history for the prompt
        history_text = ""
        for msg in history[-6:]:  # Last 6 messages for context
            role = msg.get('role', 'unknown')
            content = msg.get('content', '')
            history_text += f"{role.upper()}: {content}\n"
        
        full_prompt = raw_prompt.format(
            history=history_text if history_text else "(Ingen historik)",
            query=query
        )
        
        try:
            resp = self.client.models.generate_content(
                model=self.model_extractor,
                contents=full_prompt,
                config=types.GenerateContentConfig(response_mime_type="application/json")
            )
            result = json.loads(resp.text)
            logger.info(f"Entity extraction complete: {result.get('extracted_entities', {})}")
            return result
        except Exception as e:
            logger.error(f"Entity extraction failed: {e}")
            return self._fallback_session_state()
    
    def _fallback_session_state(self) -> Dict:
        """Fallback state when extraction fails - with multi-resource structure"""
        return {
            "extracted_entities": {
                "resources": [],  # List of resources
                "location": None,
                "volume": None,
                "start_date": None,
                "price_cap": None
            },
            "missing_info": ["resources"],
            "current_intent": "INSPIRATION",
            "confidence": 0.0
        }

    def _merge_session_state(self, old_state: Dict, new_extract: Dict) -> Dict:
        """
        Smart merge av gammal state och ny extraktion för att förhindra att data försvinner.
        Prioriterar ny data vid konflikter, men behåller gammal data om ny saknas.
        """
        if not old_state or not old_state.get('extracted_entities'):
            return new_extract

        old_entities = old_state.get('extracted_entities', {})
        new_entities = new_extract.get('extracted_entities', {})
        
        merged_entities = {
            "resources": [],
            "location": new_entities.get('location') or old_entities.get('location'),
            "volume": new_entities.get('volume') or old_entities.get('volume'),
            "start_date": new_entities.get('start_date') or old_entities.get('start_date'),
            "price_cap": new_entities.get('price_cap') or old_entities.get('price_cap')
        }

        # --- RESOURCE MERGE LOGIC ---
        old_res_map = {}
        for r in old_entities.get('resources', []):
            key = r.get('role', '').lower()
            if key:
                old_res_map[key] = r.copy()

        processed_roles = set()
        
        for new_r in new_entities.get('resources', []):
            role_key = new_r.get('role', '').lower()
            
            if role_key in old_res_map:
                existing = old_res_map[role_key]
                if new_r.get('level'): existing['level'] = new_r['level']
                if new_r.get('quantity'): existing['quantity'] = new_r['quantity']
                existing['status'] = new_r.get('status', existing['status'])
                existing['dialog_status'] = new_r.get('dialog_status', existing['dialog_status'])
                merged_entities['resources'].append(existing)
                processed_roles.add(role_key)
            else:
                merged_entities['resources'].append(new_r)

        # BEHÅLL GAMLA RESURSER SOM INTE NÄMNDES (Anti-Purge)
        for role_key, old_r in old_res_map.items():
            if role_key not in processed_roles:
                merged_entities['resources'].append(old_r)

        return {
            "extracted_entities": merged_entities,
            "missing_info": new_extract.get('missing_info', []),
            "current_intent": new_extract.get('current_intent', 'INSPIRATION'),
            "confidence": new_extract.get('confidence', 0.0)
        }

    def _plan_query(self, query: str, history: List[Dict]) -> Dict:
        """Steg 1: Planner - Identifierar Process-steg"""
        raw_prompt = self.prompts.get('planner', {}).get('instruction', '')
        
        # Injicera dagens datum
        prompt = raw_prompt.format(date=datetime.date.today())
        
        full_prompt = f"{prompt}\n\nHISTORIK: {history[-2:]}\nANVÄNDARENS FRÅGA: {query}"
        
        try:
            resp = self.client.models.generate_content(
                model=self.model_planner,
                contents=full_prompt,
                config=types.GenerateContentConfig(response_mime_type="application/json")
            )
            return json.loads(resp.text)
        except Exception as e:
            logger.error(f"Planning failed: {e}")
            # Fallback plan
            return {
                "reasoning": "Fallback due to error",
                "target_step": "general",
                "target_type": "DEFINITION",
                "vector_query": query
            }

    def _search_lake(self, target_step: str, target_type: str, allowed_authorities: List[str] = None) -> Dict[str, Dict]:
        """Steg 2: Hunter - Söker filer baserat på Planner's Step/Type med authority filter"""
        if allowed_authorities is None:
            allowed_authorities = ["PRIMARY", "SECONDARY"]
            
        hits = {}
        if not target_step: return hits
        
        # Smart filnamns-sökning: "step_3_volume_RULE_*.md"
        # Vi använder glob mönster för att hitta rätt filer direkt
        pattern = f"{target_step}*{target_type}*.md"
        
        # Fallback: Om planner säger "ALL", sök bredare
        if target_type == "ALL": pattern = f"{target_step}*.md"
            
        logger.info(f"Hunter scanning lake for: {pattern} (allowed authorities: {allowed_authorities})")
        
        for file_path in PATHS['lake'].glob(pattern):
            try:
                # Vi läser in hela filen (Frontmatter + Content)
                with open(file_path, 'r', encoding='utf-8') as f:
                    raw_content = f.read()
                
                # Parse frontmatter to check authority_level
                parts = raw_content.split("---", 2)
                if len(parts) >= 3:
                    try:
                        frontmatter = yaml.safe_load(parts[1])
                        authority = frontmatter.get('authority_level', 'UNKNOWN')
                    except:
                        authority = 'UNKNOWN'
                    content = parts[2].strip()
                else:
                    content = raw_content
                    authority = 'UNKNOWN'
                
                # KILLSWITCH: Skip if authority not in allowed list
                if authority not in allowed_authorities:
                    logger.debug(f"🚫 BLOCKED {file_path.name} (authority: {authority} not in {allowed_authorities})")
                    continue
                    
                doc_id = file_path.stem
                hits[doc_id] = {
                    "id": doc_id,
                    "filename": file_path.name,
                    "content": content,
                    "source": "HUNTER (Direct Hit)",
                    "type": target_type,
                    "authority": authority
                }
            except Exception:
                continue
                
        # Begränsa Hunter om den hittar för mycket (max 5 relevanta regler)
        return dict(list(hits.items())[:5])

    def _search_vector(self, query: str, filter_step: str = None, allowed_authorities: List[str] = None) -> Dict[str, Dict]:
        """Steg 3: Vector - Semantisk sökning med authority filter"""
        if allowed_authorities is None:
            allowed_authorities = ["PRIMARY", "SECONDARY"]
            
        hits = {}
        if not self.collection: return hits
        
        # Build where clause with step AND authority filter
        conditions = []
        
        if filter_step and filter_step != "general":
            conditions.append({"step": filter_step})
        
        # Authority filter (KILLSWITCH)
        if len(allowed_authorities) == 1:
            # Single authority - use simple equality
            conditions.append({"authority": allowed_authorities[0]})
        else:
            # Multiple authorities - use $in operator
            conditions.append({"authority": {"$in": allowed_authorities}})
        
        # Combine conditions
        if len(conditions) == 1:
            where_clause = conditions[0]
        elif len(conditions) > 1:
            where_clause = {"$and": conditions}
        else:
            where_clause = None
            
        try:
            logger.info(f"Vector search with filter: {where_clause}")
            res = self.collection.query(
                query_texts=[query],
                n_results=10,
                where=where_clause
            )
            
            if not res['ids']: return hits
            
            for i, doc_id in enumerate(res['ids'][0]):
                meta = res['metadatas'][0][i]
                hits[doc_id] = {
                    "id": doc_id,
                    "filename": meta.get('filename', 'unknown'),
                    "content": res['documents'][0][i],
                    "source": "VECTOR",
                    "type": meta.get('type', 'UNKNOWN'),
                    "authority": meta.get('authority', 'UNKNOWN')
                }
        except Exception as e:
            logger.error(f"Vector search failed: {e}")
            
        return hits

    def _synthesize(self, query: str, context_docs: List[str], extracted_entities: Dict = None, target_step: str = None) -> str:
        """Steg 5: Syntes - med fas-specifik persona och injicerad session state"""
        
        # DYNAMIC PROMPT SELECTION based on target_step
        if target_step in ['step_1_intake', 'step_1_needs']:
            prompt_key = 'synthesizer_intake'
        elif target_step in ['step_2_level', 'step_3_volume']:
            prompt_key = 'synthesizer_protocol'
        elif target_step == 'step_4_strategy':
            prompt_key = 'synthesizer_strategy'
        else:
            prompt_key = 'synthesizer_intake'  # Default fallback
        
        raw_prompt = self.prompts.get(prompt_key, {}).get('instruction', '')
        
        # Fallback to generic synthesizer if specific prompt is missing
        if not raw_prompt:
            logger.warning(f"Prompt '{prompt_key}' not found, falling back to 'synthesizer'")
            raw_prompt = self.prompts.get('synthesizer', {}).get('instruction', '')
        
        logger.info(f"Using persona: {prompt_key} for step: {target_step}")
        
        prompt = raw_prompt.format(context_docs="\n\n".join(context_docs))
        
        # Inject extracted entities into prompt to prevent re-asking
        entity_context = ""
        if extracted_entities:
            known = {k: v for k, v in extracted_entities.items() if v is not None}
            if known:
                entity_context = f"\n\nKÄND INFORMATION (fråga INTE efter detta igen):\n{json.dumps(known, ensure_ascii=False, indent=2)}"
        
        try:
            resp = self.client.models.generate_content(
                model=self.model_synthesizer,
                contents=f"{prompt}{entity_context}\n\nFRÅGA: {query}"
            )
            return resp.text
        except Exception as e:
            return f"Ett fel uppstod vid generering av svaret: {e}"

    def run(self, query: str, history: List[Dict] = [], session_state: Dict = None) -> Dict[str, Any]:
        """Main Pipeline with State Persistence"""
        logger.info(f"New Query: {query}")
        
        # 0. EXTRACT (Delta från senaste meddelandet)
        extracted_delta = self._extract_session_state(query, history)
        
        # 0.5 MERGE (Slå ihop med befintlig state från frontend)
        current_state = self._merge_session_state(session_state, extracted_delta)
        
        current_intent = current_state.get('current_intent', 'INSPIRATION')
        extracted_entities = current_state.get('extracted_entities', {})
        logger.info(f"Merged State Resources: {len(extracted_entities.get('resources', []))}")
        logger.info(f"Current Intent: {current_intent}, Missing: {current_state.get('missing_info')}")
        
        # KILLSWITCH LOGIC: Determine allowed authority levels based on intent
        if current_intent == "FACT":
            allowed_authorities = ["PRIMARY"]
            logger.info("🛡️ GHOST MODE ACTIVATED: Blocking SECONDARY files based on intent 'FACT'")
        else:
            allowed_authorities = ["PRIMARY", "SECONDARY"]
        
        # 1. PLAN
        plan = self._plan_query(query, history)
        target_step = plan.get('target_step', 'general')
        target_type = plan.get('target_type', 'DEFINITION')
        
        candidates = {}
        
        # 2. HUNT (Om vi letar efter regler/instruktioner) - med authority filter
        # Hunter är bra på att hämta "ALLA regler för steg 3"
        if target_type in ['RULE', 'INSTRUCTION', 'DATA_POINTER']:
            hunter_hits = self._search_lake(target_step, target_type, allowed_authorities)
            candidates.update(hunter_hits)
            
        # 3. VECTOR (Förståelse) - med authority filter
        vector_query = plan.get('vector_query', query)
        vector_hits = self._search_vector(vector_query, target_step, allowed_authorities)
        
        # Slå ihop (Vector fyller på där Hunter missar)
        for k, v in vector_hits.items():
            if k not in candidates:
                candidates[k] = v
        
        # 4. CONTEXT PREP (Skippar Judge i denna version för snabbhet, litar på Planner)
        context_docs = []
        sources = []
        
        # Sortera: Regler först!
        sorted_candidates = sorted(
            candidates.values(), 
            key=lambda x: 0 if x['type'] == 'RULE' else 1
        )
        
        for doc in sorted_candidates[:8]: # Max 8 block context
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
            
        # 5. SYNTHESIZE (med extracted_entities och target_step för persona-val)
        answer = self._synthesize(query, context_docs, extracted_entities, target_step)
        
        # --- BLACK BOX RECORDER (Loggning) ---
        try:
            # 1. Bestäm vilken Persona som användes
            if target_step in ['step_1_intake', 'step_1_needs']:
                used_persona = 'synthesizer_intake'
            elif target_step in ['step_2_level', 'step_3_volume']:
                used_persona = 'synthesizer_protocol'
            elif target_step == 'step_4_strategy':
                used_persona = 'synthesizer_strategy'
            else:
                used_persona = 'synthesizer_intake (fallback)'

            # 2. Bygg logg-objektet
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
                    "hunter_hits": len(hunter_hits) if 'hunter_hits' in locals() else 0,
                    "vector_hits": len(vector_hits) if 'vector_hits' in locals() else 0,
                    "final_sources": sources
                },
                "output": {
                    "response_length": len(answer),
                    "response_preview": answer[:100] + "..." if answer else ""
                }
            }

            # 3. Skriv till dagens loggfil (JSONL)
            # OBS: PATHS['logs'] är en fil, så vi använder .parent för mappen
            log_dir = PATHS['logs'].parent
            log_filename = f"session_trace_{datetime.date.today()}.jsonl"
            log_path = log_dir / log_filename
            
            # Säkerställ att log-mappen finns
            log_dir.mkdir(parents=True, exist_ok=True)

            with open(log_path, 'a', encoding='utf-8') as log_file:
                log_file.write(json.dumps(trace_entry, ensure_ascii=False) + "\n")
                
        except Exception as log_error:
            logger.error(f"Failed to write session trace: {log_error}")

        return {
            "response": answer,
            "sources": list(set(sources)),
            "thoughts": plan,
            "current_state": current_state
        }

# Singleton för import
engine = AddaSearchEngine()