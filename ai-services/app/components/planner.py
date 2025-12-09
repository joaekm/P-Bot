"""
Planner Component v5.24 - Logic Layer + Entity Extraction

Pipeline placering:
    IntentAnalyzer → ContextBuilder → [Planner] → AvropsContainerManager → Synthesizer
         ↓               ↓               ↓
       intent          context          plan

IN:  intent: dict, context: dict, avrop: dict, history: list
OUT: dict med:
    {
        "primary_conclusion": "Kärnsvaret",
        "tone_instruction": "Helpful/Guiding",
        "target_step": "step_1_intake",
        "missing_info": ["volume", "start_date"],
        "entity_changes": [
            {"action": "ADD", "type": "resource", "data": {"roll": "Projektledare", "level": 4}},
            {"action": "UPDATE", "type": "global", "field": "location_text", "value": "Stockholm"}
        ],
        "strategic_input": "Fritext insikt för fas 1/4"
    }

Ansvar:
- Analysera context och skapa plan för Synthesizer
- Extrahera entiteter från användarens query (entity_changes)
- Generera strategic_input för fas 1 och 4
- Validera stegövergångar (forward-only)
"""
import json
import logging
import re
import yaml
from pathlib import Path
from typing import List, Dict, Optional, Tuple

from google.genai import types

logger = logging.getLogger("ADDA_ENGINE")


class PrimaryRuleValidator:
    """Validates entities against PRIMARY rules only."""
    
    def __init__(self, lake_dir: Path = None):
        if lake_dir is None:
            base_dir = Path(__file__).resolve().parent.parent.parent
            lake_dir = base_dir / "storage" / "lake"
        
        self.lake_dir = lake_dir
        self.constraints: List[Dict] = []
        self._load_primary_rules()
    
    def _load_primary_rules(self):
        """Load constraints from PRIMARY files only."""
        self.constraints = []
        
        if not self.lake_dir.exists():
            return
        
        for md_file in self.lake_dir.glob("*.md"):
            if "SECONDARY" in md_file.name:
                continue
            
            try:
                with open(md_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                if content.startswith("---"):
                    parts = content.split("---", 2)
                    if len(parts) >= 3:
                        frontmatter = yaml.safe_load(parts[1])
                        if not frontmatter:
                            continue
                        
                        authority = frontmatter.get("authority_level", "UNKNOWN")
                        if authority != "PRIMARY":
                            continue
                        
                        if "constraints" in frontmatter:
                            for constraint in frontmatter["constraints"]:
                                constraint["source"] = md_file.name
                                self.constraints.append(constraint)
                        
            except Exception:
                pass
    
    def validate(self, avrop: Dict) -> Tuple[List[str], Optional[str]]:
        """Validate avrop against PRIMARY rules."""
        warnings = []
        forced_strategy = None
        
        # Validate volume (320-hour rule)
        volume = avrop.get("volume")
        if volume:
            volume_int = int(volume) if isinstance(volume, (int, float)) else None
            if volume_int and volume_int > 320:
                warnings.append(f"Volym {volume_int}h överstiger 320h-gränsen → FKU krävs")
                forced_strategy = "FKU"
        
        # Validate resources (level 5 → FKU)
        for resource in avrop.get("resources", []):
            level = resource.get("level")
            if level == 5:
                warnings.append(f"Kompetensnivå 5 (Expert) kräver FKU")
                forced_strategy = "FKU"
        
        return warnings, forced_strategy


_rule_validator: Optional[PrimaryRuleValidator] = None

def _get_rule_validator() -> PrimaryRuleValidator:
    global _rule_validator
    if _rule_validator is None:
        _rule_validator = PrimaryRuleValidator()
    return _rule_validator


class PlannerComponent:
    """
    Planner - Logic Layer + Entity Extraction.
    
    v5.24: Returns pure dict, handles entity extraction.
    """
    
    STEP_ORDER = ['step_1_intake', 'step_2_level', 'step_3_volume', 'step_4_strategy', 'complete']
    
    def __init__(self, client, model: str, prompts: Dict):
        self.client = client
        self.model = model
        self.prompts = prompts
        self.system_prompt = prompts.get('planner', {}).get('system_prompt', '')
        
        if not self.system_prompt:
            raise ValueError("KRITISKT: planner.system_prompt saknas i assistant_prompts.yaml")
    
    def create_plan(
        self, 
        intent: Dict, 
        context: Dict,
        avrop: Dict = None,
        history: List[Dict] = None,
        current_step: str = "step_1_intake"
    ) -> Dict:
        """
        Analyze context and create plan with entity changes.
        
        Args:
            intent: dict from IntentAnalyzer {branches, search_terms, query}
            context: dict from ContextBuilder {documents: [...]}
            avrop: current avrop dict (shopping cart)
            history: conversation history
            current_step: current process step
            
        Returns:
            Dict with plan, entity_changes, strategic_input
        """
        avrop = avrop or {}
        history = history or []
        
        # Validate against rules
        validator = _get_rule_validator()
        validation_warnings, forced_strategy = validator.validate(avrop)
        
        # Prepare context summary
        context_summary = self._format_context(context)
        
        # Build prompt
        prompt = self._build_prompt(intent, context_summary, avrop, history, current_step)
        
        try:
            resp = self.client.models.generate_content(
                model=self.model,
                contents=prompt,
                config=types.GenerateContentConfig(response_mime_type="application/json")
            )
            
            result = json.loads(resp.text)
            
            # Validate step transition
            llm_target_step = result.get('target_step', current_step)
            validated_step = self._validate_step_transition(current_step, llm_target_step)
            
            plan = {
                "primary_conclusion": result.get('primary_conclusion', 'Ingen slutsats'),
                "tone_instruction": result.get('tone_instruction', 'Helpful/Guiding'),
                "target_step": validated_step,
                "missing_info": result.get('missing_info', []),
                "policy_check": result.get('policy_check', ''),
                "conflict_resolution": result.get('conflict_resolution'),
                "data_validation": result.get('data_validation'),
                "validation_warnings": validation_warnings,
                "forced_strategy": forced_strategy,
                "entity_changes": result.get('entity_changes', []),
                "strategic_input": result.get('strategic_input', ''),
                "primary_sources": result.get('primary_sources', []),
                "secondary_sources": result.get('secondary_sources', [])
            }
            
            logger.info(f"Plan: tone={plan['tone_instruction']}, step={plan['target_step']}, "
                       f"entities={len(plan['entity_changes'])}")
            
            return plan
            
        except Exception as e:
            logger.error(f"Planner failed: {e}")
            return self._fallback_plan(intent, avrop, validation_warnings, forced_strategy)
    
    def _format_context(self, context: Dict) -> str:
        """Format context documents for LLM."""
        docs = context.get("documents", [])
        if not docs:
            return "(Inga dokument hittade)"
        
        lines = [f"DOKUMENT ({len(docs)} st):"]
        for doc in docs[:10]:  # Max 10
            lines.append(f"\n[{doc.get('type', '?')}] {doc.get('filename', 'unknown')}")
            content = doc.get('content', '')
            # Include full content, no truncation
            lines.append(content)
        
        return "\n".join(lines)
    
    def _build_prompt(
        self, 
        intent: Dict, 
        context_summary: str,
        avrop: Dict,
        history: List[Dict],
        current_step: str
    ) -> str:
        """Build the full prompt for LLM."""
        
        # History context
        history_text = ""
        if history:
            for msg in history[-6:]:
                role = msg.get('role', 'unknown').upper()
                content = msg.get('content', '')
                history_text += f"{role}: {content}\n"
        
        # Current avrop summary
        avrop_summary = f"""
AKTUELL VARUKORG:
- Resurser: {len(avrop.get('resources', []))}
- Plats: {avrop.get('location_text', '-')}
- Region: {avrop.get('region', '-')}
- Volym: {avrop.get('volume', '-')} timmar
- Startdatum: {avrop.get('start_date', '-')}
- Slutdatum: {avrop.get('end_date', '-')}
"""
        for res in avrop.get('resources', []):
            avrop_summary += f"  • [{res.get('id', '?')}] {res.get('roll', '?')} (nivå {res.get('level', '?')}) x{res.get('antal', 1)}\n"
        
        # Step constraints
        try:
            current_idx = self.STEP_ORDER.index(current_step)
        except ValueError:
            current_idx = 0
        
        allowed_steps = [current_step]
        if current_idx + 1 < len(self.STEP_ORDER):
            allowed_steps.append(self.STEP_ORDER[current_idx + 1])
        allowed_steps.append('general')
        
        prompt = f"""{self.system_prompt}

--- INTENT ---
Fråga: "{intent.get('query', '')}"
Branches: {intent.get('branches', [])}
Söktermer: {intent.get('search_terms', [])}

--- KONVERSATIONSHISTORIK ---
{history_text if history_text else "(Första meddelandet)"}

{avrop_summary}

--- CONTEXT (Hämtade dokument) ---
{context_summary}

--- STEG-KONTROLL ---
NUVARANDE STEG: {current_step}
TILLÅTNA NÄSTA STEG: {allowed_steps}

Analysera och returnera JSON med:
- primary_conclusion
- tone_instruction
- target_step (ett av: {allowed_steps})
- missing_info (lista)
- entity_changes (lista med entiteter att lägga till/uppdatera/ta bort)
- strategic_input (strategisk insikt för fas 1 och 4)
"""
        return prompt
    
    def _validate_step_transition(self, current_step: str, proposed_step: str) -> str:
        """Validate step transition."""
        if proposed_step == 'general':
            return proposed_step
        
        try:
            current_idx = self.STEP_ORDER.index(current_step)
        except ValueError:
            current_idx = 0
        
        try:
            proposed_idx = self.STEP_ORDER.index(proposed_step)
        except ValueError:
            return current_step
        
        # Allow backward movement (previously blocked)
        if proposed_idx < current_idx:
            logger.info(f"Allowing backward: {proposed_step} <- {current_step}")
            return proposed_step
            
        # Block skipping multiple steps forward
        if proposed_idx > current_idx + 1:
            logger.warning(f"Blocked skip: {current_step} -> {proposed_step}")
            return current_step
        
        return proposed_step
    
    def _fallback_plan(
        self, 
        intent: Dict, 
        avrop: Dict,
        validation_warnings: List[str],
        forced_strategy: Optional[str]
    ) -> Dict:
        """Create fallback plan when LLM fails."""
        return {
            "primary_conclusion": "Kunde inte analysera automatiskt",
            "tone_instruction": "Helpful/Guiding",
            "target_step": "step_1_intake",
            "missing_info": [],
            "policy_check": "Fallback",
            "conflict_resolution": None,
            "data_validation": None,
            "validation_warnings": validation_warnings,
            "forced_strategy": forced_strategy,
            "entity_changes": [],
            "strategic_input": "",
            "primary_sources": [],
            "secondary_sources": []
        }
    
