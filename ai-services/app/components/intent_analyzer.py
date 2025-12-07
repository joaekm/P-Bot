"""
Intent Analyzer Component - Query to Search Strategy (v5.5)
Maps user queries to IntentTarget with search strategy and taxonomy coordinates.
Uses LLM for intelligent search planning.

v5.5 Changes:
- Removed entity extraction (moved to Synthesizer)
- Removed hardcoded ROLE_MAPPING, LOCATION_MAPPING, DELETE_PATTERNS
- Now LLM-driven for search strategy and search terms
- Returns search_strategy and search_terms for ContextBuilder
"""
import json
import logging
from typing import List, Dict, Optional

from google.genai import types

from ..models import (
    IntentTarget,
    TaxonomyRoot,
    TaxonomyBranch,
    ScopeContext,
    VALID_BRANCHES,
)
from ..services import VocabularyService

logger = logging.getLogger("ADDA_ENGINE")


class IntentAnalyzerComponent:
    """
    Intent Analyzer - Maps user queries to search strategy.
    
    v5.5: Now LLM-driven for intelligent search planning.
    
    Pipeline:
    1. Use LLM to analyze query and determine search strategy
    2. Return IntentTarget with search_strategy, search_terms, branches
    3. ContextBuilder uses this to fetch relevant documents
    
    NO entity extraction here - that's Synthesizer's job.
    """
    
    def __init__(self, client, model: str, prompts: Dict):
        self.client = client
        self.model = model
        self.prompts = prompts
        self.vocabulary = VocabularyService()
        
        # Load prompt template from config
        intent_config = prompts.get('intent_analyzer', {})
        self.system_prompt = intent_config.get('system_prompt', '')
        
        if not self.system_prompt:
            logger.warning("No intent_analyzer.system_prompt found, using default")
            self.system_prompt = self._default_system_prompt()
    
    def analyze(self, query: str, history: List[Dict] = None) -> IntentTarget:
        """
        Analyze query using LLM and return IntentTarget with search strategy.
        
        Args:
            query: User's current query
            history: Conversation history (optional)
            
        Returns:
            IntentTarget with search_strategy, search_terms, branches, intent
        """
        # Build context from vocabulary
        vocab_context = self.vocabulary.get_prompt_context()
        
        # Format history for prompt - include more context for reference resolution
        history_text = ""
        last_bot_message = ""
        last_topic = ""
        
        if history:
            # v5.11: Full history - no truncation (Gemini has 1M token context)
            for msg in history:
                role = msg.get('role', 'unknown')
                content = msg.get('content', '')  # Full content
                history_text += f"{role.upper()}: {content}\n"
                
                # Track last bot message for reference resolution
                if role.lower() in ['assistant', 'bot', 'ai']:
                    last_bot_message = content
                    
                    # Detect if bot made a recommendation
                    if any(kw in content.lower() for kw in ['rekommenderar', 'föreslår', 'bör välja', 'passar bäst']):
                        last_topic = "RECOMMENDATION"
                    elif any(kw in content.lower() for kw in ['prismodell', 'utvärderingsmodell']):
                        last_topic = "PRICING_MODEL"
                    elif any(kw in content.lower() for kw in ['nivå', 'kompetensnivå']):
                        last_topic = "LEVEL"
                    elif any(kw in content.lower() for kw in ['roll', 'konsult', 'utvecklare', 'projektledare']):
                        last_topic = "ROLE"
        
        # Build context hint for reference resolution
        context_hint = ""
        if last_topic:
            context_hint = f"""
SENASTE KONTEXT (för att förstå referenser som "det", "detta", "den"):
- Senaste ämne: {last_topic}
- Botens senaste meddelande: {last_bot_message[:200]}

Om användaren säger "ja", "det blir bra", "rekommendera mig" etc., refererar de troligen till ämnet ovan.
"""
        
        # Build the prompt
        prompt = f"""{self.system_prompt}

VOCABULARY (kända begrepp i systemet):
{vocab_context}

KONVERSATIONSHISTORIK:
{history_text if history_text else "(Första meddelandet)"}
{context_hint}

ANVÄNDARENS FRÅGA:
{query}

VIKTIGT: Om frågan innehåller referenser som "det", "detta", "den", "rekommendera mig" - titta på konversationshistoriken för att förstå vad användaren syftar på!

Returnera JSON:
"""
        
        try:
            resp = self.client.models.generate_content(
                model=self.model,
                contents=prompt,
                config=types.GenerateContentConfig(response_mime_type="application/json")
            )
            
            result = json.loads(resp.text)
            
            # Parse LLM response
            intent_target = self._parse_llm_response(query, result)
            
            logger.info(f"Intent Analysis (LLM): {intent_target.intent_category}, "
                       f"branches={[b.value for b in intent_target.taxonomy_branches]}, "
                       f"search_terms={intent_target.search_terms[:3]}, "
                       f"strategy={intent_target.search_strategy}")
            
            return intent_target
            
        except Exception as e:
            logger.error(f"LLM intent analysis failed: {e}, using fallback")
            return self._fallback_analysis(query)
    
    def _parse_llm_response(self, query: str, result: Dict) -> IntentTarget:
        """Parse LLM response into IntentTarget."""
        # Parse branches
        branches = []
        for b in result.get("taxonomy_branches", ["ROLES"]):
            try:
                branches.append(TaxonomyBranch(b))
            except ValueError:
                pass
        
        if not branches:
            branches = [TaxonomyBranch.ROLES]
        
        # Parse search strategy
        search_strategy = result.get("search_strategy", {
            "lake": True,
            "vector": True,
            "graph": False
        })
        
        # Parse search terms
        search_terms = result.get("search_terms", [])
        if not search_terms:
            # Extract key terms from query as fallback
            search_terms = [w for w in query.split() if len(w) > 3][:5]
        
        # Parse intent
        intent_category = result.get("intent_category", "INSPIRATION")
        if intent_category not in ["FACT", "INSPIRATION", "INSTRUCTION"]:
            intent_category = "INSPIRATION"
        
        # Determine scope based on intent
        scope_preference = self._determine_scope(intent_category, branches)
        
        # Get roots from branches
        taxonomy_roots = self._roots_from_branches(branches)
        
        return IntentTarget(
            original_query=query,
            taxonomy_roots=taxonomy_roots,
            taxonomy_branches=branches,
            detected_topics=result.get("detected_topics", []),
            detected_entities=result.get("detected_entities", []),
            scope_preference=scope_preference,
            intent_category=intent_category,
            confidence=result.get("confidence", 0.7),
            search_strategy=search_strategy,
            search_terms=search_terms
        )
    
    def _fallback_analysis(self, query: str) -> IntentTarget:
        """Fallback analysis when LLM fails."""
        query_lower = query.lower()
        
        # Simple intent classification
        if any(kw in query_lower for kw in ["vad är", "hur mycket", "kostar", "måste"]):
            intent = "FACT"
        elif any(kw in query_lower for kw in ["hjälp", "exempel", "tips"]):
            intent = "INSPIRATION"
        else:
            intent = "INSPIRATION"
        
        # Simple branch detection
        branches = [TaxonomyBranch.ROLES]
        if any(kw in query_lower for kw in ["pris", "takpris", "timmar", "volym"]):
            branches.append(TaxonomyBranch.FINANCIALS)
        if any(kw in query_lower for kw in ["fku", "avrop", "strategi"]):
            branches.append(TaxonomyBranch.STRATEGY)
        
        # Extract search terms from query
        search_terms = [w for w in query.split() if len(w) > 3][:5]
        
        return IntentTarget(
            original_query=query,
            taxonomy_roots=self._roots_from_branches(branches),
            taxonomy_branches=branches[:3],
            detected_topics=[],
            detected_entities=[],
            scope_preference=self._determine_scope(intent, branches),
            intent_category=intent,
            confidence=0.4,
            search_strategy={"lake": True, "vector": True, "graph": False},
            search_terms=search_terms
        )
    
    def _determine_scope(self, intent: str, branches: List[TaxonomyBranch]) -> List[ScopeContext]:
        """Determine scope preference based on intent and branches."""
        if intent == "FACT":
            return [ScopeContext.FRAMEWORK_SPECIFIC]
        
        if TaxonomyBranch.GOVERNANCE in branches:
            return [ScopeContext.FRAMEWORK_SPECIFIC, ScopeContext.GENERAL_LEGAL]
        
        if intent == "INSPIRATION":
            return [
                ScopeContext.FRAMEWORK_SPECIFIC,
                ScopeContext.DOMAIN_KNOWLEDGE,
                ScopeContext.GENERAL_LEGAL
            ]
        
        return [ScopeContext.FRAMEWORK_SPECIFIC, ScopeContext.DOMAIN_KNOWLEDGE]
    
    def _roots_from_branches(self, branches: List[TaxonomyBranch]) -> List[TaxonomyRoot]:
        """Determine taxonomy roots from detected branches."""
        roots = set()
        for branch in branches:
            for root, valid in VALID_BRANCHES.items():
                if branch in valid:
                    roots.add(root)
                    break
        return list(roots)
    
    def _default_system_prompt(self) -> str:
        """Default system prompt if none configured."""
        return """Du är Intent Analyzer för Addas upphandlingssystem.

Din uppgift är att analysera användarens fråga och bestämma:
1. VAR ska vi söka information? (lake/vector/graph)
2. VILKA söktermer ska användas?
3. VILKEN typ av fråga är det? (FACT/INSPIRATION/INSTRUCTION)
4. VILKA taxonomy branches är relevanta?

REGLER:
- FACT = Användaren vill veta regler, priser, villkor (t.ex. "Vad är takpriset?")
- INSPIRATION = Användaren vill ha hjälp, exempel (t.ex. "Hur formulerar jag detta?")
- INSTRUCTION = Användaren vill ha steg-för-steg-guide

BRANCHES:
- ROLES: Konsultroller, kompetenser, nivåer
- FINANCIALS: Priser, takpris, volym, timmar
- LOCATIONS: Regioner, orter, anbudsområden
- GOVERNANCE: Regler, lagar, krav, GDPR
- STRATEGY: FKU, direktavrop, avropsformer
- ARTIFACTS: Dokument, mallar, CV, avtal
- PHASES: Processsteg, faser

SEARCH STRATEGY:
- lake: true om vi behöver söka i markdown-filer
- vector: true om vi behöver semantisk sökning
- graph: true om vi behöver relationer mellan begrepp

OUTPUT JSON:
{
  "intent_category": "FACT" | "INSPIRATION" | "INSTRUCTION",
  "taxonomy_branches": ["ROLES", "FINANCIALS", ...],
  "search_strategy": {"lake": true, "vector": true, "graph": false},
  "search_terms": ["sökterm1", "sökterm2", ...],
  "detected_topics": ["topic1", "topic2"],
  "detected_entities": ["entity1", "entity2"],
  "confidence": 0.0-1.0
}"""
