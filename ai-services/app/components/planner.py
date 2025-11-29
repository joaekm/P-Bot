"""
Planner Component - Query Analysis & Search Strategy
Analyzes user queries and determines the search strategy.
"""
import json
import logging
import datetime
from typing import List, Dict

from google.genai import types

logger = logging.getLogger("ADDA_ENGINE")


class PlannerComponent:
    """
    Planner - Identifies process step and block type for search.
    
    Outputs:
    - reasoning: Why this step/type was chosen
    - target_step: Which process step to search (step_1_intake, step_2_level, etc.)
    - target_type: What type of block to look for (RULE, INSTRUCTION, DEFINITION, etc.)
    - vector_query: Optimized search string
    """
    
    def __init__(self, client, model: str, prompts: Dict):
        self.client = client
        self.model = model
        self.prompts = prompts
    
    def plan(self, query: str, history: List[Dict]) -> Dict:
        """Analyze query and create search plan."""
        raw_prompt = self.prompts.get('planner', {}).get('instruction', '')
        
        # Inject today's date
        prompt = raw_prompt.format(date=datetime.date.today())
        
        full_prompt = f"{prompt}\n\nHISTORIK: {history[-2:]}\nANVÄNDARENS FRÅGA: {query}"
        
        try:
            resp = self.client.models.generate_content(
                model=self.model,
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

