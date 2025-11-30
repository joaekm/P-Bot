"""
Planner Component - Logic Layer (Reasoning)
Analyzes context and creates a ReasoningPlan for Synthesizer.

This is the "thinking" step between context retrieval and response generation.
The Planner:
1. Analyzes retrieved context
2. Resolves conflicts between sources (PRIMARY > SECONDARY)
3. Validates data against rules (e.g., 320-hour rule)
4. Creates a strategy for how Synthesizer should respond
"""
import json
import logging
import datetime
from typing import List, Dict, Optional

from google.genai import types

from ..models import IntentTarget, ReasoningPlan, ReasoningContext

logger = logging.getLogger("ADDA_ENGINE")


class PlannerComponent:
    """
    Planner (Logic Layer) - Reasoning before Synthesis.
    
    Input: IntentTarget + Context (from ContextBuilder)
    Output: ReasoningPlan (for Synthesizer)
    
    The Planner does NOT generate user-facing text.
    It creates a logical analysis that guides the Synthesizer.
    """
    
    def __init__(self, client, model: str, prompts: Dict):
        self.client = client
        self.model = model
        self.prompts = prompts
        self.system_prompt = prompts.get('planner', {}).get('system_prompt', '')
        
        if not self.system_prompt:
            logger.warning("No planner.system_prompt found in config")
    
    def create_plan(
        self, 
        intent: IntentTarget, 
        context: Dict[str, Dict]
    ) -> ReasoningPlan:
        """
        Analyze context and create reasoning plan for Synthesizer.
        
        Args:
            intent: IntentTarget from IntentAnalyzer
            context: Dict of doc_id -> doc_data from ContextBuilder
            
        Returns:
            ReasoningPlan with logical analysis and strategy
        """
        # 1. Prepare structured context summary
        reasoning_context = self._prepare_context(context)
        context_summary = self._format_context_for_llm(context, reasoning_context)
        
        # 2. Build prompt
        prompt = self._build_prompt(intent, context_summary, reasoning_context)
        
        # 3. Call LLM for reasoning
        try:
            resp = self.client.models.generate_content(
                model=self.model,
                contents=prompt,
                config=types.GenerateContentConfig(response_mime_type="application/json")
            )
            
            result = json.loads(resp.text)
            
            # Helper to convert "null" string to None
            def clean_null(val):
                if val == "null" or val == "None":
                    return None
                return val
            
            # 4. Parse to ReasoningPlan
            plan = ReasoningPlan(
                primary_conclusion=result.get('primary_conclusion', 'Ingen slutsats kunde dras'),
                policy_check=result.get('policy_check', 'Ingen specifik regel identifierad'),
                tone_instruction=result.get('tone_instruction', 'Informative'),
                missing_info=result.get('missing_info', []),
                conflict_resolution=clean_null(result.get('conflict_resolution')),
                data_validation=clean_null(result.get('data_validation')),
                target_step=result.get('target_step', self._derive_step(intent)),
                primary_sources=result.get('primary_sources', []),
                secondary_sources=result.get('secondary_sources', [])
            )
            
            logger.info(f"Reasoning Plan: tone={plan.tone_instruction}, "
                       f"step={plan.target_step}, "
                       f"conflicts={plan.has_conflicts()}, "
                       f"warning={plan.requires_warning()}")
            
            return plan
            
        except Exception as e:
            logger.error(f"Reasoning failed: {e}")
            return self._fallback_plan(intent, context)
    
    def _prepare_context(self, context: Dict[str, Dict]) -> ReasoningContext:
        """Prepare structured context summary."""
        primary_docs = []
        secondary_docs = []
        framework_count = 0
        legal_count = 0
        rule_count = 0
        
        for doc_id, doc in context.items():
            authority = doc.get('authority', 'UNKNOWN')
            scope = doc.get('scope_context', '')
            doc_type = doc.get('type', '')
            
            doc_summary = {
                'id': doc_id,
                'filename': doc.get('filename', ''),
                'type': doc_type,
                'scope': scope,
                'content_preview': doc.get('content', '')[:300]
            }
            
            if authority == 'PRIMARY':
                primary_docs.append(doc_summary)
            else:
                secondary_docs.append(doc_summary)
            
            if scope == 'FRAMEWORK_SPECIFIC':
                framework_count += 1
            elif scope == 'GENERAL_LEGAL':
                legal_count += 1
            
            if doc_type == 'RULE':
                rule_count += 1
        
        return ReasoningContext(
            primary_docs=primary_docs,
            secondary_docs=secondary_docs,
            framework_specific_count=framework_count,
            general_legal_count=legal_count,
            rule_count=rule_count,
            has_conflicting_scopes=(framework_count > 0 and legal_count > 0)
        )
    
    def _format_context_for_llm(
        self, 
        context: Dict[str, Dict], 
        reasoning_context: ReasoningContext
    ) -> str:
        """Format context documents for LLM consumption."""
        lines = []
        
        # Summary
        lines.append(f"SAMMANFATTNING:")
        lines.append(f"- PRIMARY-dokument: {len(reasoning_context.primary_docs)}")
        lines.append(f"- SECONDARY-dokument: {len(reasoning_context.secondary_docs)}")
        lines.append(f"- RULE-dokument: {reasoning_context.rule_count}")
        lines.append(f"- Konflikt mellan scopes: {'JA' if reasoning_context.has_conflicting_scopes else 'NEJ'}")
        lines.append("")
        
        # PRIMARY documents first (most important)
        if reasoning_context.primary_docs:
            lines.append("--- PRIMARY DOKUMENT (TRUMFAR) ---")
            for doc in reasoning_context.primary_docs[:5]:  # Max 5
                lines.append(f"\n[{doc['type']}] {doc['filename']}")
                lines.append(f"Scope: {doc['scope']}")
                lines.append(f"Innehåll: {doc['content_preview']}...")
        
        # SECONDARY documents (if allowed)
        if reasoning_context.secondary_docs:
            lines.append("\n--- SECONDARY DOKUMENT (REFERENS) ---")
            for doc in reasoning_context.secondary_docs[:3]:  # Max 3
                lines.append(f"\n[{doc['type']}] {doc['filename']}")
                lines.append(f"Scope: {doc['scope']}")
                lines.append(f"Innehåll: {doc['content_preview']}...")
        
        return "\n".join(lines)
    
    def _build_prompt(
        self, 
        intent: IntentTarget, 
        context_summary: str,
        reasoning_context: ReasoningContext
    ) -> str:
        """Build the full prompt for LLM reasoning."""
        
        # Add conflict warning if needed
        conflict_warning = ""
        if reasoning_context.has_conflicting_scopes:
            conflict_warning = """
⚠️ KONFLIKT DETEKTERAD: Både FRAMEWORK_SPECIFIC och GENERAL_LEGAL dokument finns.
Du MÅSTE ange i conflict_resolution vilken källa som gäller och varför.
"""
        
        prompt = f"""
{self.system_prompt}

{conflict_warning}

--- INTENT (Vad användaren vill) ---
Kategori: {intent.intent_category}
Fråga: "{intent.original_query}"
Detekterade topics: {intent.detected_topics}
Detekterade entities: {intent.detected_entities}
Taxonomy branches: {[b.value for b in intent.taxonomy_branches]}
Ghost Mode (blockera SECONDARY): {intent.should_block_secondary()}

--- CONTEXT (Hämtade dokument) ---
{context_summary}

Analysera och returnera din ReasoningPlan som JSON.
"""
        return prompt
    
    def _derive_step(self, intent: IntentTarget) -> str:
        """Derive process step from IntentTarget branches."""
        branches = [b.value for b in intent.taxonomy_branches]
        
        if 'STRATEGY' in branches:
            return 'step_4_strategy'
        elif 'FINANCIALS' in branches:
            return 'step_3_volume'
        elif 'ROLES' in branches or 'LOCATIONS' in branches:
            return 'step_1_intake'
        elif 'GOVERNANCE' in branches:
            return 'step_2_level'  # Often about competence requirements
        else:
            return 'general'
    
    def _fallback_plan(
        self, 
        intent: IntentTarget, 
        context: Dict[str, Dict]
    ) -> ReasoningPlan:
        """Create fallback plan when LLM reasoning fails."""
        # Extract sources from context
        primary_sources = [
            doc.get('filename', '') 
            for doc in context.values() 
            if doc.get('authority') == 'PRIMARY'
        ]
        secondary_sources = [
            doc.get('filename', '') 
            for doc in context.values() 
            if doc.get('authority') == 'SECONDARY'
        ]
        
        return ReasoningPlan(
            primary_conclusion="Kunde inte analysera kontexten automatiskt. Baserar svaret på tillgängliga dokument.",
            policy_check="Fallback - ingen specifik regel identifierad",
            tone_instruction="Helpful/Guiding",
            missing_info=["Automatisk analys misslyckades"],
            conflict_resolution=None,
            data_validation=None,
            target_step=self._derive_step(intent),
            primary_sources=primary_sources[:5],
            secondary_sources=secondary_sources[:3]
        )
    
    # =========================================================================
    # LEGACY METHOD (for backward compatibility)
    # =========================================================================
    
    def plan(self, query: str, history: List[Dict]) -> Dict:
        """
        Legacy method for backward compatibility.
        Creates a simple search plan without full reasoning.
        """
        raw_prompt = self.prompts.get('planner', {}).get('instruction', '')
        
        if not raw_prompt:
            return {
                "reasoning": "No planner instruction found",
                "target_step": "general",
                "target_type": "DEFINITION",
                "vector_query": query
            }
        
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
            logger.error(f"Legacy planning failed: {e}")
            return {
                "reasoning": "Fallback due to error",
                "target_step": "general",
                "target_type": "DEFINITION",
                "vector_query": query
            }
