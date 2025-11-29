"""
Extractor Component - Entity Extraction & State Management
Handles extraction of structured data from conversation history.
"""
import json
import logging
from typing import List, Dict

from google.genai import types

logger = logging.getLogger("ADDA_ENGINE")


class ExtractorComponent:
    """
    Entity Extraction - Creates a "Shadow State" from conversation history.
    
    Extracts:
    - extracted_entities: structured data about the procurement
    - missing_info: list of what's still needed
    - current_intent: FACT (rules) or INSPIRATION (help/examples)
    """
    
    def __init__(self, client, model: str, prompts: Dict):
        self.client = client
        self.model = model
        self.prompts = prompts
    
    def extract(self, query: str, history: List[Dict]) -> Dict:
        """Extract session state from query and history."""
        raw_prompt = self.prompts.get('extractor', {}).get('instruction', '')
        
        if not raw_prompt:
            logger.warning("Extractor prompt not found in assistant_prompts.yaml")
            return self._fallback_state()
        
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
                model=self.model,
                contents=full_prompt,
                config=types.GenerateContentConfig(response_mime_type="application/json")
            )
            result = json.loads(resp.text)
            logger.info(f"Entity extraction complete: {result.get('extracted_entities', {})}")
            return result
        except Exception as e:
            logger.error(f"Entity extraction failed: {e}")
            return self._fallback_state()
    
    def _fallback_state(self) -> Dict:
        """Fallback state when extraction fails - with multi-resource structure"""
        return {
            "extracted_entities": {
                "resources": [],
                "location": None,
                "volume": None,
                "start_date": None,
                "price_cap": None
            },
            "missing_info": ["resources"],
            "current_intent": "INSPIRATION",
            "confidence": 0.0
        }
    
    def merge(self, old_state: Dict, new_extract: Dict) -> Dict:
        """
        Smart merge of old state and new extraction to prevent data loss.
        Prioritizes new data on conflicts, but keeps old data if new is missing.
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

        # KEEP OLD RESOURCES NOT MENTIONED (Anti-Purge)
        for role_key, old_r in old_res_map.items():
            if role_key not in processed_roles:
                merged_entities['resources'].append(old_r)

        return {
            "extracted_entities": merged_entities,
            "missing_info": new_extract.get('missing_info', []),
            "current_intent": new_extract.get('current_intent', 'INSPIRATION'),
            "confidence": new_extract.get('confidence', 0.0)
        }

