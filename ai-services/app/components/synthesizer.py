"""
Synthesizer Component - Response Generation & Entity Extraction (v5.6)
Generates AI responses and extracts/updates entities from conversation.

v5.6 Changes:
- Added current date injection to prevent outdated date references
- Added proper completion summary flow with user confirmation
- Added "Senior" → Level 4-5 inference for role extraction
- Improved missing fields context from RequiredFields (not LLM guessing)

v5.5 Changes:
- Entity extraction moved here from IntentAnalyzer
- Returns SynthesizerResult with response + avrop_changes
- Understands DELETE operations ("ta bort X", "vi behöver inte X längre")
- Uses "thinking model" (Pro) for better context understanding

The Synthesizer receives a ReasoningPlan from the Planner which contains:
- primary_conclusion: The logical answer
- policy_check: Which rule governed the decision
- tone_instruction: How to phrase the response
- missing_info: What's still needed
"""
import json
import logging
import re
from datetime import date, datetime
from dateutil.relativedelta import relativedelta
from typing import List, Dict, Optional, Tuple
from pydantic import BaseModel, Field

from google.genai import types

from ..models import (
    ReasoningPlan, 
    AvropsData, 
    AvropsProgress,
    Resurs,
    Region,
    EntityAction, 
    EntityChange,
    Prismodell,
    Utvarderingsmodell,
)

logger = logging.getLogger("ADDA_ENGINE")


# v5.8: Location to Region mapping for automatic region assignment
# When user mentions a city, we map it to the correct Anbudsområde
LOCATION_TO_REGION = {
    # Region A - Stockholm
    "stockholm": Region.A,
    "solna": Region.A,
    "sundbyberg": Region.A,
    "nacka": Region.A,
    "lidingö": Region.A,
    "huddinge": Region.A,
    "täby": Region.A,
    "sollentuna": Region.A,
    "kista": Region.A,
    
    # Region B - Östra Mellansverige
    "uppsala": Region.B,
    "eskilstuna": Region.B,
    "västerås": Region.B,
    "örebro": Region.B,
    "linköping": Region.B,
    "norrköping": Region.B,
    
    # Region C - Småland med öarna
    "jönköping": Region.C,
    "växjö": Region.C,
    "kalmar": Region.C,
    "visby": Region.C,
    "gotland": Region.C,
    
    # Region D - Sydsverige
    "malmö": Region.D,
    "lund": Region.D,
    "helsingborg": Region.D,
    "kristianstad": Region.D,
    "halmstad": Region.D,
    
    # Region E - Västsverige
    "göteborg": Region.E,
    "gothenburg": Region.E,
    "borås": Region.E,
    "trollhättan": Region.E,
    "uddevalla": Region.E,
    "skövde": Region.E,
    
    # Region F - Norra Mellansverige
    "gävle": Region.F,
    "falun": Region.F,
    "borlänge": Region.F,
    "mora": Region.F,
    "sundsvall": Region.F,
    
    # Region G - Mellersta och Övre Norrland
    "umeå": Region.G,
    "luleå": Region.G,
    "kiruna": Region.G,
    "östersund": Region.G,
    "skellefteå": Region.G,
}

# Human-readable region names for confirmation messages
REGION_NAMES = {
    Region.A: "Anbudsområde A (Stockholm)",
    Region.B: "Anbudsområde B (Östra Mellansverige)",
    Region.C: "Anbudsområde C (Småland med öarna)",
    Region.D: "Anbudsområde D (Sydsverige)",
    Region.E: "Anbudsområde E (Västsverige)",
    Region.F: "Anbudsområde F (Norra Mellansverige)",
    Region.G: "Anbudsområde G (Mellersta och Övre Norrland)",
}


class SynthesizerResult(BaseModel):
    """Result from Synthesizer - response + entity changes."""
    response: str = Field(..., description="Generated response text")
    avrop_changes: List[EntityChange] = Field(
        default_factory=list,
        description="Changes to apply to AvropsData (ADD/UPDATE/DELETE)"
    )
    updated_avrop: Optional[AvropsData] = Field(
        default=None,
        description="Updated AvropsData after applying changes"
    )


class SynthesizerComponent:
    """
    Synthesizer - Generates responses and extracts entities.
    
    v5.5: Now responsible for entity extraction (moved from IntentAnalyzer).
    v5.6: Added missing_fields injection and completion detection.
    
    Personas:
    - synthesizer_intake: Coaching, curious (for needs/roles phase)
    - synthesizer_protocol: Efficient, auditor-like (for volume/price phase)
    - synthesizer_strategy: Advisory, concluding (for strategy phase)
    
    The Synthesizer uses the ReasoningPlan to:
    1. Know the logical conclusion (what to say)
    2. Know the tone (how to say it)
    3. Know what's missing (what to ask) - NOW from RequiredFields, not LLM!
    4. Extract/Update entities from conversation (NEW in v5.5)
    """
    
    # Patterns that indicate user confirmation
    CONFIRMATION_PATTERNS = [
        r'\b(ja|japp|jepp|yes|ok|okej|okay)\b.*\b(korrekt|stämmer|rätt|bra|gå vidare|fortsätt|initiera|slutför|klart)\b',
        r'\b(det\s+)?stämmer\b',
        r'\b(korrekt|rätt|exakt)\b',
        r'\bgå\s+vidare\b',
        r'\bslutför\b',
        r'\binitiera\b',
        r'\bdet\s+är\s+klart\b',
        r'\bvi\s+kör\b',
    ]
    
    def __init__(self, client, model: str, prompts: Dict):
        self.client = client
        self.model = model
        self.prompts = prompts
    
    def _detect_user_confirmation(self, query: str) -> bool:
        """Detect if user is confirming/approving the current state."""
        query_lower = query.lower().strip()
        
        for pattern in self.CONFIRMATION_PATTERNS:
            if re.search(pattern, query_lower):
                return True
        
        # Simple "ja" or "yes" as standalone
        if query_lower in ['ja', 'ja!', 'japp', 'jepp', 'yes', 'ok', 'okej', 'korrekt']:
            return True
        
        return False
    
    def generate_response(
        self, 
        query: str,
        plan: ReasoningPlan, 
        context: Dict[str, Dict],
        current_avrop: Optional[AvropsData] = None,
        history: List[Dict] = None
    ) -> SynthesizerResult:
        """
        Generate response and extract entities.
        
        v5.5: Now returns SynthesizerResult with both response and avrop_changes.
        
        Args:
            query: Original user query
            plan: ReasoningPlan with logical analysis
            context: Dict of doc_id -> doc_data from ContextBuilder
            current_avrop: Current AvropsData (shopping cart)
            history: Conversation history
            
        Returns:
            SynthesizerResult with response and avrop_changes
        """
        # 1. Select persona based on target_step from plan
        prompt_key = self._select_persona(plan.target_step)
        raw_prompt = self._get_prompt(prompt_key)
        
        logger.info(f"Synthesizer: persona={prompt_key}, tone={plan.tone_instruction}")
        
        # 2. Format context documents
        context_docs = self._format_context(context)
        
        # 3. Build reasoning injection
        reasoning_injection = self._build_reasoning_injection(plan)
        
        # 4. Build entity context (current avrop state)
        entity_context = self._build_avrop_context(current_avrop)
        
        # 5. Build missing fields context (THE KEY FIX - v5.6)
        missing_context = self._build_missing_fields_context(current_avrop, query)
        
        # 6. Build history context (v5.8: include avrop for date calculation context)
        history_context = self._build_history_context(history, current_avrop)
        
        # 7. Build final prompt with entity extraction instructions
        prompt = raw_prompt.format(context_docs=context_docs)
        
        # 8. Build date context (v5.6 - bot needs to know current date)
        today = date.today()
        date_validation = self.prompts.get('synthesizer_date_validation', {}).get('instruction', '')
        date_context = f"DAGENS DATUM: {today.isoformat()} ({today.strftime('%d %B %Y')})\n\n{date_validation}"
        
        # 9. Get entity extraction rules from config
        entity_extraction = self.prompts.get('synthesizer_entity_extraction', {}).get('instruction', '')
        
        full_prompt = f"""
{prompt}

{date_context}

{reasoning_injection}

{entity_context}

{missing_context}

{history_context}

FRÅGA: {query}

---
{entity_extraction}

Skriv först ditt naturliga svar, sedan JSON-blocket.
"""
        
        try:
            resp = self.client.models.generate_content(
                model=self.model,
                contents=full_prompt
            )
            
            response_text = resp.text
            
            # 7. Extract entity changes from response
            avrop_changes, clean_response = self._extract_entity_changes(response_text)
            
            # 8. Apply changes to avrop
            updated_avrop = self._apply_changes(current_avrop, avrop_changes)
            
            # Note: data_validation is internal info for Synthesizer, not shown to user
            # The Synthesizer prompt already includes this info for tone/content guidance
            
            logger.info(f"Synthesizer: {len(avrop_changes)} entity changes extracted")
            
            return SynthesizerResult(
                response=clean_response,
                avrop_changes=avrop_changes,
                updated_avrop=updated_avrop
            )
            
        except Exception as e:
            logger.error(f"Synthesis failed: {e}")
            return SynthesizerResult(
                response=f"Ett fel uppstod vid generering av svaret: {e}",
                avrop_changes=[],
                updated_avrop=current_avrop
            )
    
    def _extract_entity_changes(self, response_text: str) -> Tuple[List[EntityChange], str]:
        """Extract entity changes JSON from response and return clean response."""
        changes = []
        clean_response = response_text
        
        # Look for JSON block in response
        json_pattern = r'```json\s*(\{.*?\})\s*```'
        match = re.search(json_pattern, response_text, re.DOTALL)
        
        if match:
            try:
                json_str = match.group(1)
                data = json.loads(json_str)
                
                for change in data.get('avrop_changes', []):
                    action = change.get('action', '').upper()
                    change_type = change.get('type', '')
                    
                    if action == 'ADD' and change_type == 'resource':
                        res_data = change.get('data', {})
                        new_res = Resurs(
                            id="",
                            roll=res_data.get('roll', 'Okänd'),
                            level=res_data.get('level'),
                            antal=res_data.get('antal', 1)
                        )
                        changes.append(EntityChange(
                            action=EntityAction.ADD,
                            target_type="resource",
                            new_resource=new_res
                        ))
                    
                    elif action == 'UPDATE' and change_type == 'resource':
                        target = change.get('target', '')
                        res_data = change.get('data', {})
                        for field, value in res_data.items():
                            changes.append(EntityChange(
                                action=EntityAction.UPDATE,
                                target_type="resource",
                                target_field=target,
                                new_value=value
                            ))
                    
                    elif action == 'DELETE' and change_type == 'resource':
                        target = change.get('target', '')
                        changes.append(EntityChange(
                            action=EntityAction.DELETE,
                            target_type="resource",
                            target_field=target
                        ))
                    
                    elif action == 'UPDATE' and change_type == 'global':
                        field = change.get('field', '')
                        value = change.get('value')
                        changes.append(EntityChange(
                            action=EntityAction.UPDATE,
                            target_type="global",
                            target_field=field,
                            new_value=value
                        ))
                
                # Remove JSON block from response
                clean_response = re.sub(json_pattern, '', response_text, flags=re.DOTALL).strip()
                
            except json.JSONDecodeError as e:
                logger.warning(f"Failed to parse entity JSON: {e}")
        
        return changes, clean_response
    
    def _apply_changes(
        self, 
        current_avrop: Optional[AvropsData], 
        changes: List[EntityChange]
    ) -> AvropsData:
        """Apply entity changes to AvropsData."""
        if current_avrop is None:
            avrop = AvropsData()
        else:
            avrop = current_avrop.model_copy(deep=True)
        
        for change in changes:
            if change.action == EntityAction.DELETE:
                if change.target_type == "resource" and change.target_field:
                    target_lower = change.target_field.lower()
                    avrop.resources = [
                        r for r in avrop.resources 
                        if target_lower not in r.roll.lower()
                    ]
                    logger.info(f"Deleted resource: {change.target_field}")
            
            elif change.action == EntityAction.ADD:
                if change.target_type == "resource" and change.new_resource:
                    # Generate unique ID
                    new_id = f"res_{len(avrop.resources) + 1}"
                    change.new_resource.id = new_id
                    
                    # v5.6: Infer level from "Senior" prefix if level not set
                    if change.new_resource.level is None:
                        role_lower = change.new_resource.roll.lower()
                        if "senior" in role_lower:
                            # Senior roles typically require level 4-5
                            # We set to 5 as a suggestion, user can adjust
                            change.new_resource.level = 5
                            logger.info(f"Inferred level 5 from 'Senior' in role: {change.new_resource.roll}")
                    
                    avrop.resources.append(change.new_resource)
                    logger.info(f"Added resource: {change.new_resource.roll}")
            
            elif change.action == EntityAction.UPDATE:
                if change.target_type == "resource" and change.target_field:
                    target_lower = change.target_field.lower()
                    for res in avrop.resources:
                        if target_lower in res.roll.lower():
                            if change.new_value is not None:
                                # Update level specifically
                                if isinstance(change.new_value, int):
                                    res.level = change.new_value
                            break
                
                elif change.target_type == "global" and change.target_field:
                    field = change.target_field
                    value = change.new_value
                    
                    # Map common field names
                    field_mapping = {
                        "location": "location_text",
                        "ort": "location_text",
                        "plats": "location_text",
                        "volym": "volume",
                        "timmar": "volume",
                        "pris": "takpris",
                        "takpris": "takpris",
                        "start": "start_date",
                        "startdatum": "start_date",
                        "slut": "end_date",
                        "slutdatum": "end_date",
                    }
                    
                    mapped_field = field_mapping.get(field.lower(), field)
                    
                    # Handle prismodell enum
                    if mapped_field == "prismodell" and value:
                        try:
                            avrop.prismodell = Prismodell(value)
                            logger.info(f"Set prismodell: {value}")
                        except ValueError:
                            logger.warning(f"Invalid prismodell value: {value}")
                    
                    # Handle utvarderingsmodell enum
                    elif mapped_field == "utvarderingsmodell" and value:
                        try:
                            avrop.utvarderingsmodell = Utvarderingsmodell(value)
                            logger.info(f"Set utvarderingsmodell: {value}")
                        except ValueError:
                            logger.warning(f"Invalid utvarderingsmodell value: {value}")
                    
                    # v5.8: Handle location -> also set region automatically
                    elif mapped_field == "location_text" and value:
                        avrop.location_text = value
                        # Try to map to region
                        location_lower = str(value).lower().strip()
                        if location_lower in LOCATION_TO_REGION:
                            avrop.region = LOCATION_TO_REGION[location_lower]
                            region_name = REGION_NAMES.get(avrop.region, avrop.region.value)
                            logger.info(f"Mapped location '{value}' to {region_name}")
                        else:
                            logger.info(f"Updated location_text: {value} (no region mapping found)")
                    
                    elif hasattr(avrop, mapped_field):
                        setattr(avrop, mapped_field, value)
                        logger.info(f"Updated global field: {mapped_field} = {value}")
        
        # v5.7: Auto-calculate end_date if start_date exists and duration mentioned
        if avrop.start_date and not avrop.end_date:
            avrop.end_date = self._calculate_end_date(avrop.start_date, changes)
        
        # Auto-detect avrop type after changes
        avrop.avrop_typ = avrop.detect_avrop_typ()
        
        return avrop
    
    def _calculate_end_date(self, start_date: str, changes: List[EntityChange]) -> Optional[str]:
        """
        Calculate end_date from start_date and duration mentioned in changes.
        
        v5.7: Handles "X månader" patterns to auto-calculate end_date.
        """
        # Look for volume that might indicate duration
        # This is a heuristic - if we have start_date and no end_date,
        # and the LLM extracted a volume, we might be able to infer duration
        
        # For now, we rely on the LLM to extract end_date directly
        # This method is a fallback for when LLM doesn't calculate it
        
        try:
            start = datetime.strptime(start_date, "%Y-%m-%d")
            
            # Check if any change mentions months
            for change in changes:
                if change.target_type == "global" and change.new_value:
                    value_str = str(change.new_value).lower()
                    
                    # Pattern: "12 månader" or "X mån"
                    month_match = re.search(r'(\d+)\s*(?:månader?|mån)', value_str)
                    if month_match:
                        months = int(month_match.group(1))
                        end = start + relativedelta(months=months)
                        # Set to last day of the month
                        end = end.replace(day=1) + relativedelta(months=1, days=-1)
                        logger.info(f"Calculated end_date from {months} months: {end.strftime('%Y-%m-%d')}")
                        return end.strftime("%Y-%m-%d")
            
            return None
            
        except (ValueError, AttributeError) as e:
            logger.warning(f"Failed to calculate end_date: {e}")
            return None
    
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
    
    def _build_avrop_context(self, avrop: Optional[AvropsData]) -> str:
        """Build avrop context to prevent re-asking and show current state."""
        if not avrop:
            return "\nNUVARANDE VARUKORG: (tom)"
        
        lines = ["\nNUVARANDE VARUKORG (fråga INTE efter detta igen):"]
        
        if avrop.resources:
            lines.append("Resurser:")
            for res in avrop.resources:
                level_str = f"Nivå {res.level}" if res.level else "Nivå ej angiven"
                lines.append(f"  - {res.roll} ({level_str}) x{res.antal}")
        
        if avrop.location_text:
            lines.append(f"Ort: {avrop.location_text}")
        if avrop.volume:
            lines.append(f"Volym: {avrop.volume} timmar")
        if avrop.start_date:
            lines.append(f"Startdatum: {avrop.start_date}")
        if avrop.takpris:
            lines.append(f"Takpris: {avrop.takpris} kr/h")
        if avrop.avrop_typ:
            lines.append(f"Avropstyp: {avrop.avrop_typ.value}")
        
        return "\n".join(lines)
    
    def _build_avrop_summary(self, avrop: AvropsData, progress: AvropsProgress) -> str:
        """
        Build a formatted summary of the current avrop for confirmation.
        
        v5.6: Used when completion is high enough to ask for confirmation.
        """
        lines = ["📋 SAMMANFATTNING AV AVROPET:"]
        lines.append("")
        
        # Resources
        if avrop.resources:
            for res in avrop.resources:
                level_str = f"Nivå {res.level}" if res.level else "nivå ej angiven"
                antal_str = f"{res.antal} st " if res.antal > 1 else ""
                lines.append(f"• Roll: {antal_str}{res.roll}, {level_str}")
        
        # Volume and dates
        if avrop.volume:
            lines.append(f"• Volym: {avrop.volume} timmar")
        if avrop.takpris:
            lines.append(f"• Takpris: {avrop.takpris} kr/h")
        if avrop.start_date:
            lines.append(f"• Startdatum: {avrop.start_date}")
        if avrop.end_date:
            lines.append(f"• Slutdatum: {avrop.end_date}")
        
        # Location
        if avrop.region:
            lines.append(f"• Region: {avrop.region.value}")
        elif avrop.location_text:
            lines.append(f"• Plats: {avrop.location_text}")
        
        # Avrop type
        if avrop.avrop_typ:
            typ_name = {
                "DR_RESURS": "Dynamisk Rangordning (snabbspåret)",
                "FKU_RESURS": "Förnyad Konkurrensutsättning (FKU)",
                "FKU_PROJEKT": "FKU Projektuppdrag"
            }.get(avrop.avrop_typ.value, avrop.avrop_typ.value)
            lines.append(f"• Avropsform: {typ_name}")
        
        # Missing fields
        if progress.missing_fields:
            lines.append("")
            lines.append(f"Saknas: {', '.join(progress.missing_fields[:3])}")
            if len(progress.missing_fields) > 3:
                lines.append(f"  ... och {len(progress.missing_fields) - 3} till")
        
        lines.append("")
        lines.append("Ska vi gå vidare med detta underlag?")
        
        return "\n".join(lines)
    
    def _build_missing_fields_context(self, avrop: Optional[AvropsData], query: str = "") -> str:
        """
        Build missing fields context to guide Synthesizer on what to ask.
        
        v5.10: REMOVED percent-based logic. Now uses ONLY is_complete (deterministic).
        Summary is shown ONLY when is_complete=True, as a final confirmation.
        
        Logic:
        1. is_complete=True + user confirms -> End conversation
        2. is_complete=True + no confirmation -> Show summary, ask for confirmation
        3. is_complete=False -> List missing fields (no summary!)
        """
        if not avrop:
            return "\n⚠️ SAKNADE FÄLT: Inget avrop påbörjat ännu."
        
        progress = AvropsProgress.calculate(avrop)
        user_confirming = self._detect_user_confirmation(query)
        
        # CASE 1: Complete + User confirms -> END
        if progress.is_complete and user_confirming:
            return "\n✅ AVSLUTA KONVERSATIONEN:\nUnderlaget är komplett och användaren har bekräftat.\nSvara kort: 'Underlaget är registrerat. Du kan nu generera avropsformuläret.'"
        
        # CASE 2: Complete + No confirmation -> Show summary ONCE, ask for confirmation
        if progress.is_complete:
            summary = self._build_avrop_summary(avrop, progress)
            return f"\n✅ UNDERLAGET ÄR KOMPLETT:\n\nVISA DENNA SAMMANFATTNING OCH FRÅGA OM BEKRÄFTELSE:\n\n{summary}"
        
        # CASE 3: NOT complete -> List missing fields (NO SUMMARY)
        # Group related fields together for natural conversation flow
        lines = ["\n⚠️ SAKNADE FÄLT:"]
        lines.append("FRÅGA OM DESSA (gruppera gärna relaterade frågor):")
        
        # Categorize fields for grouping
        level_fields = [f for f in progress.missing_fields 
                       if "level" in f.lower() or "nivå" in f.lower() or "kompetensomrade" in f.lower()]
        volume_fields = [f for f in progress.missing_fields if "volume" in f.lower() or "timmar" in f.lower()]
        date_fields = [f for f in progress.missing_fields if "date" in f.lower() or "datum" in f.lower()]
        region_fields = [f for f in progress.missing_fields if "region" in f.lower()]
        strategy_fields = [f for f in progress.missing_fields 
                          if "prismodell" in f.lower() or "utvarderingsmodell" in f.lower()]
        other_fields = [f for f in progress.missing_fields 
                       if f not in level_fields and f not in volume_fields 
                       and f not in date_fields and f not in region_fields
                       and f not in strategy_fields]
        
        # Group 1: Resource-related (level + kompetensområde)
        if level_fields:
            lines.append(f"\n  RESURS-INFO (fråga tillsammans):")
            for field in level_fields[:2]:
                lines.append(f"    - {field}")
        
        # Group 2: Time-related (volume + dates)
        time_fields = volume_fields + date_fields
        if time_fields:
            lines.append(f"\n  TID & VOLYM (fråga tillsammans):")
            for field in time_fields[:3]:
                lines.append(f"    - {field}")
        
        # Group 3: Location
        if region_fields:
            lines.append(f"\n  PLATS:")
            for field in region_fields[:1]:
                lines.append(f"    - {field}")
        
        # Group 4: Strategy fields (prismodell, utvärdering)
        if strategy_fields:
            lines.append(f"\n  STRATEGI (fråga tillsammans):")
            for field in strategy_fields[:2]:
                lines.append(f"    - {field}")
        
        # Group 5: Other fields
        if other_fields:
            lines.append(f"\n  ÖVRIGT:")
            for field in other_fields[:2]:
                lines.append(f"    - {field}")
        
        lines.append("\nTIPS: Ställ 2-3 relaterade frågor samtidigt för naturligare konversation.")
        
        return "\n".join(lines)
    
    def _build_history_context(self, history: List[Dict] = None, current_avrop: Optional[AvropsData] = None) -> str:
        """
        Build conversation history context with recommendation detection.
        
        v5.7: Enhanced to detect bot recommendations for confirmation logic.
        v5.8: Added start_date context for end_date calculation.
        """
        if not history:
            return ""
        
        lines = ["\nKONVERSATIONSHISTORIK (senaste meddelanden):"]
        last_recommendation = None
        recommendation_type = None
        
        for msg in history[-6:]:  # Last 6 messages for more context
            role = msg.get('role', 'unknown').upper()
            content = msg.get('content', '')[:300]  # More content
            lines.append(f"{role}: {content}")
            
            # Detect bot recommendations
            if role in ['ASSISTANT', 'BOT', 'AI']:
                content_lower = content.lower()
                
                # Detect prismodell recommendation
                if any(kw in content_lower for kw in ['rekommenderar', 'föreslår', 'bör välja']):
                    if 'löpande' in content_lower or 'fast timpris' in content_lower:
                        last_recommendation = "LOPANDE"
                        recommendation_type = "prismodell"
                    elif 'fast pris' in content_lower and 'timpris' not in content_lower:
                        last_recommendation = "FAST_PRIS"
                        recommendation_type = "prismodell"
                    elif 'bästa förhållande' in content_lower or 'pris och kvalitet' in content_lower:
                        last_recommendation = "PRIS_70_KVALITET_30"
                        recommendation_type = "utvarderingsmodell"
                    elif 'lägsta pris' in content_lower or '100% pris' in content_lower:
                        last_recommendation = "PRIS_100"
                        recommendation_type = "utvarderingsmodell"
        
        # Add recommendation context for entity extraction
        if last_recommendation and recommendation_type:
            lines.append("")
            lines.append(f"⚠️ SENASTE REKOMMENDATION: {recommendation_type}={last_recommendation}")
            lines.append("Om användaren bekräftar med 'ja', 'bra', 'okej' → extrahera denna som UPDATE!")
        
        # v5.8: Add start_date context for end_date calculation
        if current_avrop and current_avrop.start_date and not current_avrop.end_date:
            lines.append("")
            lines.append(f"⚠️ DATUMBERÄKNING: start_date={current_avrop.start_date}")
            lines.append("Om användaren nämner 'X månader' → beräkna end_date baserat på start_date ovan!")
            lines.append("Exempel: start_date=2026-01-01 + 12 månader → end_date=2026-12-31")
        
        return "\n".join(lines)
    
    def _build_entity_context(self, extracted_entities: Optional[Dict]) -> str:
        """Legacy: Build entity context from dict format."""
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
