"""
Planner Component - Logic Layer (Reasoning)
Analyzes context and creates a ReasoningPlan for Synthesizer.

This is the "thinking" step between context retrieval and response generation.
The Planner:
1. Analyzes retrieved context
2. Resolves conflicts between sources (PRIMARY > SECONDARY)
3. Validates data against rules (e.g., 320-hour rule) - ONLY PRIMARY rules
4. Creates a strategy for how Synthesizer should respond

v5.3: Added _validate_against_rules (absorbed from normalizer.py)
"""
import json
import logging
import re
import yaml
from pathlib import Path
from typing import List, Dict, Optional, Any, Tuple

from google.genai import types

from ..models import IntentTarget, ReasoningPlan, ReasoningContext

logger = logging.getLogger("ADDA_ENGINE")


# =============================================================================
# RULE VALIDATION (absorbed from normalizer.py)
# Only loads PRIMARY rules, ignoring SECONDARY
# =============================================================================

class PrimaryRuleValidator:
    """
    Validates entities against PRIMARY rules only.
    Ignores SECONDARY rules to prevent the "Papegoj-effekten".
    """
    
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
            logger.warning(f"Lake directory not found: {self.lake_dir}")
            return
        
        for md_file in self.lake_dir.glob("*.md"):
            # CRITICAL: Skip SECONDARY files entirely
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
                        
                        # Double-check authority_level
                        authority = frontmatter.get("authority_level", "UNKNOWN")
                        if authority != "PRIMARY":
                            continue
                        
                        if "constraints" in frontmatter:
                            for constraint in frontmatter["constraints"]:
                                constraint["source"] = md_file.name
                                self.constraints.append(constraint)
                        
            except Exception as e:
                logger.debug(f"Could not parse {md_file.name}: {e}")
        
        logger.info(f"Loaded {len(self.constraints)} PRIMARY constraints (SECONDARY ignored)")
    
    def validate(self, normalized_entities: Dict) -> Tuple[List[str], Optional[str]]:
        """
        Validate normalized entities against PRIMARY rules.
        
        Returns:
            Tuple of (warnings, forced_strategy)
        """
        warnings = []
        forced_strategy = None
        
        # Validate volume (320-hour rule)
        volume = normalized_entities.get("volume")
        if volume is not None:
            volume_int = self._parse_volume(volume)
            if volume_int:
                result = self._check_volume(volume_int)
                if result:
                    warnings.append(result["message"])
                    if result.get("force_strategy"):
                        forced_strategy = result["force_strategy"]
        
        # Validate resources (level constraints)
        resources = normalized_entities.get("resources", [])
        for resource in resources:
            level = resource.get("level")
            if level is not None:
                result = self._check_level(level, resource.get("role"))
                if result:
                    warnings.append(result["message"])
                    if result.get("force_strategy"):
                        forced_strategy = result["force_strategy"]
        
        return warnings, forced_strategy
    
    def _parse_volume(self, volume) -> Optional[int]:
        """Parse volume to int."""
        if isinstance(volume, (int, float)):
            return int(volume)
        if isinstance(volume, str):
            match = re.search(r'(\d+)', volume)
            if match:
                return int(match.group(1))
        return None
    
    def _check_volume(self, volume_hours: int) -> Optional[Dict]:
        """Check volume against 320-hour rule."""
        for constraint in self.constraints:
            if constraint.get("param") == "volume_hours":
                operator = constraint.get("operator", "").upper()
                threshold = constraint.get("value", 320)
                
                if operator in ("GT", "MAX") and volume_hours > threshold:
                    return {
                        "message": constraint.get("error_msg", f"Volym {volume_hours}h överstiger {threshold}h-gränsen"),
                        "force_strategy": "FKU" if "FKU" in constraint.get("action", "") else None,
                        "source": constraint.get("source")
                    }
        
        # Hardcoded fallback: 320-hour rule (always applies)
        if volume_hours > 320:
            return {
                "message": f"Volym {volume_hours}h överstiger 320h-gränsen → FKU krävs",
                "force_strategy": "FKU",
                "source": "320-timmarsregeln (ramavtal)"
            }
        
        return None
    
    def _check_level(self, level: int, role: str = None) -> Optional[Dict]:
        """Check competence level against rules (e.g., KN5 → FKU)."""
        for constraint in self.constraints:
            if constraint.get("param") == "competence_level":
                operator = constraint.get("operator", "").upper()
                threshold = constraint.get("value", 5)
                
                if operator == "EQUALS" and level == threshold:
                    return {
                        "message": constraint.get("error_msg", f"Nivå {level} kräver FKU"),
                        "force_strategy": "FKU" if "FKU" in constraint.get("action", "") else None,
                        "source": constraint.get("source")
                    }
        
        # Hardcoded fallback: Level 5 → FKU
        if level == 5:
            return {
                "message": f"Kompetensnivå 5 (Expert) kräver FKU",
                "force_strategy": "FKU",
                "source": "KN5-regeln (ramavtal)"
            }
        
        return None


# Singleton instance
_rule_validator: Optional[PrimaryRuleValidator] = None

def _get_rule_validator() -> PrimaryRuleValidator:
    global _rule_validator
    if _rule_validator is None:
        _rule_validator = PrimaryRuleValidator()
    return _rule_validator


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
        # 0. Validate against PRIMARY rules (absorbed from normalizer.py)
        validation_warnings, forced_strategy = self._validate_against_rules(
            intent.normalized_entities
        )
        
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
            
            # 4. Parse to ReasoningPlan (with validation results)
            plan = ReasoningPlan(
                primary_conclusion=result.get('primary_conclusion', 'Ingen slutsats kunde dras'),
                policy_check=result.get('policy_check', 'Ingen specifik regel identifierad'),
                tone_instruction=result.get('tone_instruction', 'Informative'),
                missing_info=result.get('missing_info', []),
                conflict_resolution=clean_null(result.get('conflict_resolution')),
                data_validation=clean_null(result.get('data_validation')),
                validation_warnings=validation_warnings,  # NEW
                forced_strategy=forced_strategy,  # NEW
                target_step=result.get('target_step', self._derive_step(intent)),
                primary_sources=result.get('primary_sources', []),
                secondary_sources=result.get('secondary_sources', [])
            )
            
            logger.info(f"Reasoning Plan: tone={plan.tone_instruction}, "
                       f"step={plan.target_step}, "
                       f"conflicts={plan.has_conflicts()}, "
                       f"warning={plan.requires_warning()}, "
                       f"forced_strategy={forced_strategy}")
            
            return plan
            
        except Exception as e:
            logger.error(f"Reasoning failed: {e}")
            return self._fallback_plan(intent, context, validation_warnings, forced_strategy)
    
    def _validate_against_rules(self, normalized_entities: Dict) -> Tuple[List[str], Optional[str]]:
        """
        Validate normalized entities against PRIMARY rules only.
        This replaces the old normalizer.validate_entities() function.
        
        Returns:
            Tuple of (validation_warnings, forced_strategy)
        """
        validator = _get_rule_validator()
        return validator.validate(normalized_entities)
    
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
        context: Dict[str, Dict],
        validation_warnings: List[str] = None,
        forced_strategy: Optional[str] = None
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
            validation_warnings=validation_warnings or [],
            forced_strategy=forced_strategy,
            target_step=self._derive_step(intent),
            primary_sources=primary_sources[:5],
            secondary_sources=secondary_sources[:3]
        )
