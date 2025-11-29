"""
Adda P-Bot Validator v5.2
Data-driven validation & normalization using Smart Blocks from Lake.
"""
import yaml
import logging
import re
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple

logger = logging.getLogger("ADDA_ENGINE")


class ConstraintValidator:
    """
    Data-driven validator that reads constraints and mappings from Smart Block markdown files.
    """
    
    def __init__(self, lake_dir: Path = None):
        if lake_dir is None:
            # Default path relative to this file
            base_dir = Path(__file__).resolve().parent.parent.parent
            lake_dir = base_dir / "storage" / "lake"
        
        self.lake_dir = lake_dir
        self.constraints_cache: List[Dict] = []
        self.entity_mappings: Dict[str, Dict[str, str]] = {}  # {'location': {'luleå': 'Anbudsområde A', ...}}
        self._load_from_lake()
    
    def _load_from_lake(self):
        """Load all constraints and entity mappings from markdown files with YAML frontmatter."""
        self.constraints_cache = []
        self.entity_mappings = {}
        
        if not self.lake_dir.exists():
            logger.warning(f"Lake directory not found: {self.lake_dir}")
            return
        
        for md_file in self.lake_dir.glob("*.md"):
            try:
                with open(md_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Parse YAML frontmatter
                if content.startswith("---"):
                    parts = content.split("---", 2)
                    if len(parts) >= 3:
                        frontmatter = yaml.safe_load(parts[1])
                        if not frontmatter:
                            continue
                        
                        # Load constraints
                        if "constraints" in frontmatter:
                            for constraint in frontmatter["constraints"]:
                                constraint["source"] = md_file.name
                                self.constraints_cache.append(constraint)
                        
                        # Load entity mappings
                        if "entity_mapping" in frontmatter:
                            mapping_data = frontmatter["entity_mapping"]
                            mapping_type = mapping_data.get("type")  # e.g., "location", "role"
                            mapping_values = mapping_data.get("values", {})
                            
                            if mapping_type and mapping_values:
                                # Merge into existing mappings (lowercase keys)
                                if mapping_type not in self.entity_mappings:
                                    self.entity_mappings[mapping_type] = {}
                                
                                for key, value in mapping_values.items():
                                    self.entity_mappings[mapping_type][key.lower()] = value
                                
                                logger.debug(f"Loaded {len(mapping_values)} mappings for '{mapping_type}' from {md_file.name}")
                        
            except Exception as e:
                logger.debug(f"Could not parse {md_file.name}: {e}")
        
        logger.info(f"Loaded {len(self.constraints_cache)} constraints, {len(self.entity_mappings)} mapping types from Lake")
    
    def get_mapping(self, mapping_type: str) -> Dict[str, str]:
        """Get mapping dictionary for a specific type (e.g., 'location', 'role')."""
        return self.entity_mappings.get(mapping_type, {})
    
    def normalize_value(self, mapping_type: str, value: str) -> str:
        """Normalize a value using the loaded mapping. Returns original if no mapping found."""
        if not value:
            return value
        
        mapping = self.get_mapping(mapping_type)
        value_lower = value.lower().strip()
        return mapping.get(value_lower, value)
    
    def validate(self, extracted_entities: Dict) -> List[Dict]:
        """
        Validate extracted entities against loaded constraints.
        Returns a list of issues found.
        """
        issues = []
        
        # Validate resources (competence_level)
        resources = extracted_entities.get("resources", [])
        for resource in resources:
            level = resource.get("level")
            if level is not None:
                try:
                    self._check_param("competence_level", int(level), issues, resource)
                except (ValueError, TypeError):
                    pass
        
        # Validate volume
        volume_raw = extracted_entities.get("volume")
        if volume_raw:
            volume_hours = self._parse_volume(volume_raw)
            if volume_hours:
                self._check_param("volume_hours", volume_hours, issues)
        
        # Validate location (after normalization)
        location = extracted_entities.get("location")
        if location:
            self._check_param("location", location, issues)
        
        # Validate contract length
        contract_length = extracted_entities.get("contract_length_months")
        if contract_length:
            try:
                self._check_param("contract_length_months", int(contract_length), issues)
            except (ValueError, TypeError):
                pass
        
        return issues
    
    def _parse_volume(self, volume_str: str) -> Optional[int]:
        """Parse volume string like '100 timmar' or '500h' to integer hours."""
        if isinstance(volume_str, (int, float)):
            return int(volume_str)
        
        match = re.search(r'(\d+)', str(volume_str))
        if match:
            return int(match.group(1))
        return None
    
    def _check_param(self, param: str, value: Any, issues: List[Dict], context: Dict = None):
        """Check a parameter value against all matching constraints."""
        for constraint in self.constraints_cache:
            if constraint.get("param") != param:
                continue
            
            operator = constraint.get("operator", "").upper()
            threshold = constraint.get("value")
            action = constraint.get("action", "WARN")
            error_msg = constraint.get("error_msg", f"Constraint violation for {param}")
            source = constraint.get("source", "unknown")
            
            violated = False
            
            if operator == "GT" and isinstance(value, (int, float)):
                violated = value > threshold
            elif operator == "MAX" and isinstance(value, (int, float)):
                violated = value > threshold
            elif operator == "MIN" and isinstance(value, (int, float)):
                violated = value < threshold
            elif operator == "EQUALS":
                violated = value == threshold
            elif operator == "ONE_OF" and isinstance(threshold, list):
                violated = value not in threshold
            elif operator == "NOT_IN" and isinstance(threshold, list):
                violated = value in threshold
            
            if violated:
                issue_type = "BLOCK" if action == "BLOCK" else "STRATEGY_FORCE" if "TRIGGER" in action else "WARN"
                
                issue = {
                    "type": issue_type,
                    "param": param,
                    "value": value,
                    "message": error_msg,
                    "action": action,
                    "source": source
                }
                
                if context:
                    issue["context"] = {
                        "role": context.get("role"),
                        "id": context.get("id")
                    }
                
                issues.append(issue)
                logger.info(f"Constraint triggered: {param}={value} -> {action} (from {source})")


# --- SINGLETON INSTANCE ---
_validator_instance: Optional[ConstraintValidator] = None


def _get_validator() -> ConstraintValidator:
    """Get or create the singleton validator instance."""
    global _validator_instance
    if _validator_instance is None:
        _validator_instance = ConstraintValidator()
    return _validator_instance


# --- PUBLIC INTERFACE ---

def normalize_entities(entities: Dict) -> Dict:
    """
    Normalize extracted entities using data-driven mappings from Lake.
    All mappings are loaded from markdown files with entity_mapping in frontmatter.
    """
    if not entities:
        return entities
    
    validator = _get_validator()
    normalized = entities.copy()
    
    # Normalize location using data-driven mapping
    location = normalized.get('location')
    if location:
        normalized['location'] = validator.normalize_value('location', location)
    
    # Normalize resources
    resources = normalized.get('resources', [])
    if resources:
        normalized_resources = []
        for resource in resources:
            normalized_resource = resource.copy()
            
            # Normalize role names using data-driven mapping
            role = normalized_resource.get('role', '')
            if role:
                normalized_role = validator.normalize_value('role', role)
                # Fallback to basic normalization if no mapping found
                if normalized_role == role:
                    normalized_role = _fallback_role_normalize(role)
                normalized_resource['role'] = normalized_role
            
            # Ensure level is int or None, clamped to 1-5
            level = normalized_resource.get('level')
            if level is not None:
                try:
                    level_int = int(level)
                    normalized_resource['level'] = max(1, min(5, level_int))
                except (ValueError, TypeError):
                    normalized_resource['level'] = None
            
            normalized_resources.append(normalized_resource)
        
        normalized['resources'] = normalized_resources
    
    return normalized


def _fallback_role_normalize(role: str) -> str:
    """Fallback role normalization for common abbreviations."""
    if not role:
        return role
    
    fallback_mapping = {
        "pl": "Projektledare",
        "pm": "Projektledare",
        "dev": "Utvecklare",
        "arkitekt": "Lösningsarkitekt",
        "testare": "Testledare",
        "ux": "UX-designer",
    }
    
    role_lower = role.lower().strip()
    return fallback_mapping.get(role_lower, role)


def validate_entities(entities: Dict) -> Tuple[Dict, List[Dict]]:
    """
    Validate entities against data-driven constraints from Smart Blocks.
    
    Returns:
        Tuple of (entities, issues) where issues is a list of constraint violations.
    """
    validator = _get_validator()
    issues = validator.validate(entities)
    
    # Attach validation results to entities for downstream use
    if issues:
        entities["_validation_issues"] = issues
        
        # Check if any issue forces FKU strategy
        for issue in issues:
            if issue.get("action", "").startswith("TRIGGER_STRATEGY"):
                entities["_forced_strategy"] = "FKU"
                logger.info(f"Strategy forced to FKU due to constraint: {issue.get('message')}")
                break
    
    return entities, issues


def reload_from_lake():
    """Force reload of constraints and mappings from disk. Useful after re-indexing."""
    global _validator_instance
    _validator_instance = None
    _get_validator()
    logger.info("Constraints and mappings reloaded from Lake")
