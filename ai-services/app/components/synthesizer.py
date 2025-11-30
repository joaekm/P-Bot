"""
Synthesizer Component - Response Generation
Generates AI responses using ReasoningPlan and context with persona-specific prompts.

The Synthesizer receives a ReasoningPlan from the Planner which contains:
- primary_conclusion: The logical answer
- policy_check: Which rule governed the decision
- tone_instruction: How to phrase the response
- missing_info: What's still needed
"""
import json
import logging
from typing import List, Dict, Optional, Union

from ..models import ReasoningPlan

logger = logging.getLogger("ADDA_ENGINE")


class SynthesizerComponent:
    """
    Synthesizer - Generates responses with phase-specific personas.
    
    Personas:
    - synthesizer_intake: Coaching, curious (for needs/roles phase)
    - synthesizer_protocol: Efficient, auditor-like (for volume/price phase)
    - synthesizer_strategy: Advisory, concluding (for strategy phase)
    
    The Synthesizer uses the ReasoningPlan to:
    1. Know the logical conclusion (what to say)
    2. Know the tone (how to say it)
    3. Know what's missing (what to ask)
    """
    
    def __init__(self, client, model: str, prompts: Dict):
        self.client = client
        self.model = model
        self.prompts = prompts
    
    def generate_response(
        self, 
        query: str,
        plan: ReasoningPlan, 
        context: Dict[str, Dict],
        extracted_entities: Optional[Dict] = None
    ) -> str:
        """
        Generate response using ReasoningPlan from Planner.
        
        Args:
            query: Original user query
            plan: ReasoningPlan with logical analysis
            context: Dict of doc_id -> doc_data from ContextBuilder
            extracted_entities: Session state entities (optional)
            
        Returns:
            Generated response text
        """
        # 1. Select persona based on target_step from plan
        prompt_key = self._select_persona(plan.target_step)
        raw_prompt = self._get_prompt(prompt_key)
        
        logger.info(f"Synthesizer: persona={prompt_key}, tone={plan.tone_instruction}")
        
        # 2. Format context documents
        context_docs = self._format_context(context)
        
        # 3. Build reasoning injection
        reasoning_injection = self._build_reasoning_injection(plan)
        
        # 4. Build entity context
        entity_context = self._build_entity_context(extracted_entities)
        
        # 5. Build final prompt
        prompt = raw_prompt.format(context_docs=context_docs)
        
        full_prompt = f"""
{prompt}

{reasoning_injection}

{entity_context}

FRÅGA: {query}
"""
        
        try:
            resp = self.client.models.generate_content(
                model=self.model,
                contents=full_prompt
            )
            
            response_text = resp.text
            
            # 6. Add warning prefix if needed
            if plan.requires_warning() and plan.data_validation:
                response_text = f"⚠️ **Observera:** {plan.data_validation}\n\n{response_text}"
            
            return response_text
            
        except Exception as e:
            logger.error(f"Synthesis failed: {e}")
            return f"Ett fel uppstod vid generering av svaret: {e}"
    
    def _build_reasoning_injection(self, plan: ReasoningPlan) -> str:
        """Build the reasoning context to inject into the prompt."""
        lines = [
            "--- LOGISK ANALYS (från Planner) ---",
            f"SLUTSATS: {plan.primary_conclusion}",
            f"REGEL: {plan.policy_check}",
            f"TON: {plan.tone_instruction}",
        ]
        
        if plan.missing_info:
            lines.append(f"SAKNAS: {', '.join(plan.missing_info)}")
        
        if plan.conflict_resolution:
            lines.append(f"KONFLIKTLÖSNING: {plan.conflict_resolution}")
        
        if plan.data_validation:
            lines.append(f"VALIDERING: {plan.data_validation}")
        
        # Tone-specific instructions
        if plan.tone_instruction == "Strict/Warning":
            lines.append("\n⚠️ INSTRUKTION: Var tydlig och bestämd. Användaren försöker göra något som inte är tillåtet.")
        elif plan.tone_instruction == "Helpful/Guiding":
            lines.append("\n💡 INSTRUKTION: Var hjälpsam och vägledande. Vi saknar information.")
        else:
            lines.append("\nℹ️ INSTRUKTION: Ge ett informativt, faktabaserat svar.")
        
        return "\n".join(lines)
    
    def _format_context(self, context: Dict[str, Dict]) -> str:
        """Format context documents for the prompt."""
        docs = []
        
        # Sort: PRIMARY first, then by type (RULE first)
        sorted_items = sorted(
            context.items(),
            key=lambda x: (
                0 if x[1].get('authority') == 'PRIMARY' else 1,
                0 if x[1].get('type') == 'RULE' else 1
            )
        )
        
        for doc_id, doc in sorted_items[:8]:  # Max 8 documents
            authority = doc.get('authority', 'UNKNOWN')
            doc_type = doc.get('type', 'UNKNOWN')
            filename = doc.get('filename', 'unknown')
            content = doc.get('content', '')
            
            docs.append(f"--- BLOCK: {doc_type} [{authority}] (File: {filename}) ---\n{content}")
        
        return "\n\n".join(docs)
    
    def _build_entity_context(self, extracted_entities: Optional[Dict]) -> str:
        """Build entity context to prevent re-asking."""
        if not extracted_entities:
            return ""
        
        known = {k: v for k, v in extracted_entities.items() if v is not None}
        if not known:
            return ""
        
        return f"\nKÄND INFORMATION (fråga INTE efter detta igen):\n{json.dumps(known, ensure_ascii=False, indent=2)}"
    
    def _get_prompt(self, prompt_key: str) -> str:
        """Get prompt with fallback."""
        raw_prompt = self.prompts.get(prompt_key, {}).get('instruction', '')
        
        if not raw_prompt:
            logger.warning(f"Prompt '{prompt_key}' not found, falling back to 'synthesizer'")
            raw_prompt = self.prompts.get('synthesizer', {}).get('instruction', '')
        
        return raw_prompt
    
    def _select_persona(self, target_step: str) -> str:
        """Select the appropriate persona based on target step."""
        if target_step in ['step_1_intake', 'step_1_needs']:
            return 'synthesizer_intake'
        elif target_step in ['step_2_level', 'step_3_volume']:
            return 'synthesizer_protocol'
        elif target_step == 'step_4_strategy':
            return 'synthesizer_strategy'
        else:
            return 'synthesizer_intake'  # Default fallback
    
    def get_persona_name(self, target_step: str) -> str:
        """Get the persona name for logging/tracing."""
        return self._select_persona(target_step)
    
    # =========================================================================
    # LEGACY METHOD (for backward compatibility)
    # =========================================================================
    
    def synthesize(
        self, 
        query: str, 
        context_docs: List[str], 
        extracted_entities: Dict = None, 
        target_step: str = None
    ) -> str:
        """
        Legacy method for backward compatibility.
        Generate response with phase-specific persona and injected session state.
        """
        # DYNAMIC PROMPT SELECTION based on target_step
        prompt_key = self._select_persona(target_step or 'general')
        raw_prompt = self._get_prompt(prompt_key)
        
        logger.info(f"Using persona: {prompt_key} for step: {target_step}")
        
        prompt = raw_prompt.format(context_docs="\n\n".join(context_docs))
        
        # Inject extracted entities into prompt to prevent re-asking
        entity_context = self._build_entity_context(extracted_entities)
        
        try:
            resp = self.client.models.generate_content(
                model=self.model,
                contents=f"{prompt}{entity_context}\n\nFRÅGA: {query}"
            )
            return resp.text
        except Exception as e:
            return f"Ett fel uppstod vid generering av svaret: {e}"
