"""
Synthesizer Component v5.24 - Förenklad Response Generation

Pipeline placering:
    IntentAnalyzer → ContextBuilder → Planner → AvropsContainerManager → [Synthesizer]
         ↓               ↓              ↓                ↓                    ↓
       intent          context         plan         updated_avrop          response

IN:  query: str, plan: dict, avrop: dict, history: list
OUT: dict med:
    {
        "response": "Textsvar till användaren"
    }

Förenkling v5.24:
- Borttaget: _extract_entity_changes() - hanteras av Planner
- Borttaget: _apply_changes() - hanteras av AvropsContainerManager
- Borttaget: Pydantic-modeller
- Förenklad: tar emot uppdaterad avrop, returnerar bara response
"""
import json
import logging
from datetime import date
from typing import List, Dict, Optional

logger = logging.getLogger("ADDA_ENGINE")


class SynthesizerComponent:
    """
    Synthesizer - Generates natural language responses.
    
    v5.24: Simplified - only generates response text.
    Entity extraction and avrop updates handled by Planner + AvropsContainerManager.
    
    Personas:
    - synthesizer_intake: Coaching, curious (for needs/roles phase)
    - synthesizer_protocol: Efficient, auditor-like (for volume/price phase)
    - synthesizer_strategy: Advisory, concluding (for strategy phase)
    """
    
    def __init__(self, client, model: str, prompts: Dict):
        self.client = client
        self.model = model
        self.prompts = prompts
    
    def generate_response(
        self, 
        query: str,
        plan: Dict, 
        context: Dict,
        avrop: Dict = None,
        history: List[Dict] = None
    ) -> Dict:
        """
        Generate natural language response.
        
        Args:
            query: Original user query
            plan: dict from Planner with conclusion, tone, strategic_input
            context: dict from ContextBuilder with documents
            avrop: current avrop dict (already updated by AvropsContainerManager)
            history: Conversation history
            
        Returns:
            Dict with response text
        """
        avrop = avrop or {}
        history = history or []
        
        # 1. Select persona based on target_step
        prompt_key = self._select_persona(plan.get('target_step', 'step_1_intake'))
        raw_prompt = self._get_prompt(prompt_key)
        
        logger.info(f"Synthesizer: persona={prompt_key}, tone={plan.get('tone_instruction')}")
        
        # 2. Format context documents
        context_text = self._format_context(context)
        
        # 3. Build reasoning injection
        reasoning = self._build_reasoning_injection(plan)
        
        # 4. Build avrop context
        avrop_context = self._build_avrop_context(avrop)
        
        # 5. Build history context
        history_text = self._build_history_context(history)
        
        # 6. Build date context
        today = date.today()
        date_context = f"DAGENS DATUM: {today.isoformat()} ({today.strftime('%d %B %Y')})"
        
        # 7. Build strategic input (from Planner)
        strategic_input = plan.get('strategic_input', '')
        strategic_section = ""
        if strategic_input and plan.get('target_step') in ['step_1_intake', 'step_4_strategy']:
            strategic_section = f"\n\n--- STRATEGISK INSIKT ---\n{strategic_input}"
        
        # 8. Build full prompt
        full_prompt = f"""
{raw_prompt}

{date_context}

{reasoning}

{avrop_context}

{history_text}

{context_text}
{strategic_section}

FRÅGA: {query}

Svara naturligt på svenska. Var hjälpsam och vägledande.
"""
        
        try:
            resp = self.client.models.generate_content(
                model=self.model,
                contents=full_prompt
            )
            
            response_text = resp.text
            
            # Clean any JSON artifacts that might leak through
            response_text = self._clean_response(response_text)
            
            logger.info(f"Synthesizer: generated {len(response_text)} chars")
            
            return {"response": response_text}
            
        except Exception as e:
            logger.error(f"Synthesis failed: {e}")
            return {"response": f"Ett fel uppstod: {e}"}
    
    def _select_persona(self, target_step: str) -> str:
        """Select prompt persona based on current process step."""
        if target_step in ['step_1_intake', 'step_1_needs']:
            return 'synthesizer_step1_behov'
        elif target_step == 'step_2_level':
            return 'synthesizer_step2_niva'
        elif target_step == 'step_3_volume':
            return 'synthesizer_step3_volym'
        elif target_step in ['step_4_strategy', 'complete']:
            return 'synthesizer_step4_avslut'
        else:
            return 'synthesizer'
    
    def _get_prompt(self, prompt_key: str) -> str:
        """Get prompt template with fallback."""
        raw_prompt = self.prompts.get(prompt_key, {}).get('instruction', '')
        
        if not raw_prompt:
            logger.warning(f"Prompt '{prompt_key}' not found, using fallback")
            raw_prompt = self.prompts.get('synthesizer', {}).get('instruction', '')
        
        if not raw_prompt:
            raw_prompt = "Du är en hjälpsam assistent för IT-konsultupphandling."
        
        return raw_prompt
    
    def _format_context(self, context: Dict) -> str:
        """Format context documents for prompt."""
        docs = context.get("documents", [])
        if not docs:
            return "--- KONTEXT ---\n(Inga relevanta dokument hittade)"
        
        lines = [f"--- KONTEXT ({len(docs)} dokument) ---"]
        for doc in docs[:10]:
            lines.append(f"\n[{doc.get('type', '?')}] {doc.get('filename', 'unknown')}")
            content = doc.get('content', '')
            lines.append(content)
        
        return "\n".join(lines)
    
    def _build_reasoning_injection(self, plan: Dict) -> str:
        """Build reasoning context from plan."""
        lines = [
            "--- REASONING (intern analys) ---",
            f"SLUTSATS: {plan.get('primary_conclusion', '-')}",
            f"REGEL: {plan.get('policy_check', '-')}",
            f"TON: {plan.get('tone_instruction', 'Helpful/Guiding')}",
        ]
        
        missing = plan.get('missing_info', [])
        if missing:
            lines.append(f"SAKNAS: {', '.join(missing)}")
        
        warnings = plan.get('validation_warnings', [])
        if warnings:
            lines.append(f"⚠️ VARNINGAR: {'; '.join(warnings)}")
        
        forced = plan.get('forced_strategy')
        if forced:
            lines.append(f"🔒 TVINGAD STRATEGI: {forced}")
        
        # Tone-specific instructions
        tone = plan.get('tone_instruction', '')
        if tone == "Strict/Warning":
            lines.append("\n⚠️ INSTRUKTION: Var tydlig och bestämd.")
        elif tone == "Helpful/Guiding":
            lines.append("\n💡 INSTRUKTION: Var hjälpsam och vägledande.")
        
        return "\n".join(lines)
    
    def _build_avrop_context(self, avrop: Dict) -> str:
        """Build current avrop state for context."""
        lines = ["--- AKTUELL VARUKORG ---"]
        
        resources = avrop.get('resources', [])
        if resources:
            lines.append(f"Resurser ({len(resources)} st):")
            for res in resources:
                roll = res.get('roll', 'Okänd')
                level = res.get('level', '?')
                antal = res.get('antal', 1)
                lines.append(f"  • {roll} (nivå {level}) x{antal}")
        else:
            lines.append("Resurser: (inga)")
        
        # Global fields
        if avrop.get('location_text'):
            lines.append(f"Plats: {avrop['location_text']}")
        if avrop.get('region'):
            lines.append(f"Region: {avrop['region']}")
        if avrop.get('anbudsomrade'):
            lines.append(f"Anbudsområde: {avrop['anbudsomrade']}")
        if avrop.get('volume'):
            lines.append(f"Volym: {avrop['volume']} timmar")
        if avrop.get('start_date'):
            lines.append(f"Start: {avrop['start_date']}")
        if avrop.get('end_date'):
            lines.append(f"Slut: {avrop['end_date']}")
        if avrop.get('takpris'):
            lines.append(f"Takpris: {avrop['takpris']} kr")
        if avrop.get('prismodell'):
            lines.append(f"Prismodell: {avrop['prismodell']}")
        if avrop.get('pris_vikt') and avrop.get('kvalitet_vikt'):
            lines.append(f"Utvärdering: {avrop['pris_vikt']}% pris / {avrop['kvalitet_vikt']}% kvalitet")
        
        return "\n".join(lines)
    
    def _build_history_context(self, history: List[Dict]) -> str:
        """Build conversation history context."""
        if not history:
            return "--- HISTORIK ---\n(Första meddelandet)"
        
        lines = ["--- HISTORIK ---"]
        for msg in history[-6:]:
            role = msg.get('role', 'unknown').upper()
            content = msg.get('content', '')
            lines.append(f"{role}: {content}")
        
        return "\n".join(lines)
    
    def _clean_response(self, response: str) -> str:
        """Remove any JSON artifacts from response."""
        import re
        
        # Remove JSON blocks
        response = re.sub(r'```json\s*\{.*?\}\s*```', '', response, flags=re.DOTALL)
        response = re.sub(r'```\s*\{.*?\}\s*```', '', response, flags=re.DOTALL)
        
        # Remove standalone JSON objects
        response = re.sub(r'\{["\']avrop_changes["\'].*?\}', '', response, flags=re.DOTALL)
        
        # Clean up whitespace
        response = re.sub(r'\n{3,}', '\n\n', response)
        
        return response.strip()
