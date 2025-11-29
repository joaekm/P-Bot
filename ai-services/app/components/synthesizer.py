"""
Synthesizer Component - Response Generation
Generates AI responses using context and persona-specific prompts.
"""
import json
import logging
from typing import List, Dict

logger = logging.getLogger("ADDA_ENGINE")


class SynthesizerComponent:
    """
    Synthesizer - Generates responses with phase-specific personas.
    
    Personas:
    - synthesizer_intake: Coaching, curious (for needs/roles phase)
    - synthesizer_protocol: Efficient, auditor-like (for volume/price phase)
    - synthesizer_strategy: Advisory, concluding (for strategy phase)
    """
    
    def __init__(self, client, model: str, prompts: Dict):
        self.client = client
        self.model = model
        self.prompts = prompts
    
    def synthesize(self, query: str, context_docs: List[str], extracted_entities: Dict = None, target_step: str = None) -> str:
        """Generate response with phase-specific persona and injected session state."""
        
        # DYNAMIC PROMPT SELECTION based on target_step
        prompt_key = self._select_persona(target_step)
        
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
                model=self.model,
                contents=f"{prompt}{entity_context}\n\nFRÅGA: {query}"
            )
            return resp.text
        except Exception as e:
            return f"Ett fel uppstod vid generering av svaret: {e}"
    
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
        persona = self._select_persona(target_step)
        if persona == 'synthesizer_intake':
            return 'synthesizer_intake'
        elif persona == 'synthesizer_protocol':
            return 'synthesizer_protocol'
        elif persona == 'synthesizer_strategy':
            return 'synthesizer_strategy'
        return 'synthesizer_intake (fallback)'

