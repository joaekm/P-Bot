"""
Intent Analyzer Component v5.24 - Förenklad dict-baserad

Pipeline placering:
    [IntentAnalyzer] → ContextBuilder → Planner → AvropsContainerManager → Synthesizer
          ↓
        intent

IN:  query: str, history: list
OUT: dict med:
    {
        "branches": ["ROLES", "LOCATIONS", ...],
        "search_terms": ["projektledare", "Stockholm"],
        "query": "original query"
    }

Förenkling v5.24:
- Borttaget: intent_category (FACT/INSPIRATION/INSTRUCTION)
- Borttaget: scope_preference
- Borttaget: Pydantic-modeller (IntentTarget, TaxonomyBranch, etc.)
- Returnerar ren dict som ContextBuilder kan använda direkt
"""
import json
import logging
from typing import List, Dict
from pathlib import Path

from google.genai import types

logger = logging.getLogger("ADDA_ENGINE")


class IntentAnalyzerComponent:
    """
    Intent Analyzer - Maps user queries to search coordinates.
    
    v5.24: Simplified to return pure dict.
    """
    
    # Valid branches (from taxonomy)
    VALID_BRANCHES = ["ROLES", "LOCATIONS", "FINANCIALS", "PROCESS", "ARTIFACTS", "GENERAL"]
    
    def __init__(self, client, model: str, prompts: Dict):
        self.client = client
        self.model = model
        self.prompts = prompts
        
        # Load taxonomy for branch validation
        self.taxonomy = self._load_taxonomy()
        
        # Load prompt template from config
        intent_config = prompts.get('intent_analyzer', {})
        self.system_prompt = intent_config.get('system_prompt', '')
        
        if not self.system_prompt:
            logger.warning("No intent_analyzer.system_prompt found, using default")
            self.system_prompt = self._default_system_prompt()
    
    def _load_taxonomy(self) -> Dict:
        """Load taxonomy for branch validation."""
        base_dir = Path(__file__).resolve().parent.parent.parent
        taxonomy_path = base_dir / "storage" / "index" / "adda_taxonomy.json"
        
        try:
            with open(taxonomy_path, 'r', encoding='utf-8') as f:
                tax = json.load(f)
                # Update valid branches from taxonomy if available
                branches = tax.get('taxonomy_branches', {}).get('values', [])
                if branches:
                    self.VALID_BRANCHES = branches
                return tax
        except Exception as e:
            logger.warning(f"Could not load taxonomy: {e}")
            return {}
    
    def analyze(self, query: str, history: List[Dict] = None) -> Dict:
        """
        Analyze query and return search coordinates.
        
        Args:
            query: User's current query
            history: Conversation history (optional)
            
        Returns:
            Dict with branches, search_terms, query
        """
        # Format history for prompt
        history_text = ""
        if history:
            for msg in history[-6:]:
                role = msg.get('role', 'unknown')
                content = msg.get('content', '')[:300]
                history_text += f"{role.upper()}: {content}\n"
        
        # Build the prompt
        prompt = f"""{self.system_prompt}

KONVERSATIONSHISTORIK:
{history_text if history_text else "(Första meddelandet)"}

ANVÄNDARENS FRÅGA:
{query}

Returnera JSON:
"""
        
        try:
            resp = self.client.models.generate_content(
                model=self.model,
                contents=prompt,
                config=types.GenerateContentConfig(response_mime_type="application/json")
            )
            
            result = json.loads(resp.text)
            intent = self._parse_response(query, result)
            
            logger.info(f"Intent: branches={intent['branches']}, terms={intent['search_terms'][:3]}")
            return intent
            
        except Exception as e:
            logger.error(f"LLM intent analysis failed: {e}, using fallback")
            return self._fallback_analysis(query)
    
    def _parse_response(self, query: str, result: Dict) -> Dict:
        """Parse LLM response into intent dict."""
        # Validate branches
        branches = []
        for b in result.get("taxonomy_branches", ["ROLES"]):
            b_upper = b.upper()
            if b_upper in self.VALID_BRANCHES:
                branches.append(b_upper)
        
        if not branches:
            branches = ["ROLES"]
        
        # Get search terms
        search_terms = result.get("search_terms", [])
        if not search_terms:
            search_terms = [w for w in query.split() if len(w) > 3][:5]
        
        return {
            "branches": branches,
            "search_terms": search_terms,
            "query": query
        }
    
    def _fallback_analysis(self, query: str) -> Dict:
        """Fallback when LLM fails."""
        query_lower = query.lower()
        
        # Simple branch detection
        branches = ["ROLES"]
        if any(kw in query_lower for kw in ["pris", "takpris", "timmar", "volym", "kostnad"]):
            branches.append("FINANCIALS")
        if any(kw in query_lower for kw in ["stockholm", "malmö", "göteborg", "region", "område", "plats"]):
            branches.append("LOCATIONS")
        if any(kw in query_lower for kw in ["fku", "avrop", "strategi", "direktavrop"]):
            branches.append("PROCESS")
        
        # Extract search terms
        search_terms = [w for w in query.split() if len(w) > 3][:5]
        
        return {
            "branches": branches[:3],
            "search_terms": search_terms,
            "query": query
        }
    
    def _default_system_prompt(self) -> str:
        """Default system prompt."""
        return """Du är Intent Analyzer för Addas upphandlingssystem.

Din uppgift är att analysera användarens fråga och bestämma:
1. VILKA taxonomy branches är relevanta?
2. VILKA söktermer ska användas?

BRANCHES (välj 1-3 relevanta):
- ROLES: Konsultroller, kompetenser, nivåer, exempelroller
- LOCATIONS: Regioner, orter, anbudsområden, län
- FINANCIALS: Priser, takpris, volym, timmar, kostnad
- PROCESS: Avropsprocessen, FKU, direktavrop, steg
- ARTIFACTS: Dokument, mallar, CV, avtal
- GENERAL: Allmänna frågor, avtalet generellt

SEARCH TERMS:
- Extrahera nyckelord från frågan
- Inkludera synonymer och relaterade termer
- Max 5 termer

OUTPUT JSON:
{
  "taxonomy_branches": ["ROLES", ...],
  "search_terms": ["term1", "term2", ...]
}"""
