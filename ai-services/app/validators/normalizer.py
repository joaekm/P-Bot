"""
Normalizer - Entity Validation & Normalization
Prepares extracted entities for business rule validation.
"""
from typing import Dict

# Region mapping (placeholder for framework-specific rules)
REGION_MAPPING = {
    # Norrland
    "härnösand": "Region Mitt",
    "sundsvall": "Region Mitt", 
    "umeå": "Region Norr",
    "luleå": "Region Norr",
    
    # Mellansverige
    "stockholm": "Region Stockholm",
    "göteborg": "Region Väst",
    "malmö": "Region Syd",
    "linköping": "Region Öst",
    "örebro": "Region Mitt",
    "västerås": "Region Mitt",
    "uppsala": "Region Stockholm",
    
    # Remote/Distans
    "remote": "Distans",
    "distans": "Distans",
    "valfri": "Valfri ort",
}


def normalize_entities(entities: Dict) -> Dict:
    """
    Normalize extracted entities to match framework requirements.
    
    Examples:
    - Location: "Härnösand" -> "Region Mitt" (framework requirement)
    - Role names: Standardize to official role catalog
    
    This is a placeholder for the business logic we'll build.
    """
    if not entities:
        return entities
    
    normalized = entities.copy()
    
    # Normalize location
    location = normalized.get('location')
    if location:
        location_lower = location.lower().strip()
        if location_lower in REGION_MAPPING:
            normalized['location'] = REGION_MAPPING[location_lower]
    
    # Normalize resources (if present)
    resources = normalized.get('resources', [])
    if resources:
        normalized_resources = []
        for resource in resources:
            normalized_resource = resource.copy()
            
            # Normalize role names (placeholder - could map to official catalog)
            role = normalized_resource.get('role', '')
            normalized_resource['role'] = _normalize_role_name(role)
            
            # Ensure level is int or None
            level = normalized_resource.get('level')
            if level is not None:
                try:
                    normalized_resource['level'] = int(level)
                except (ValueError, TypeError):
                    normalized_resource['level'] = None
            
            normalized_resources.append(normalized_resource)
        
        normalized['resources'] = normalized_resources
    
    return normalized


def _normalize_role_name(role: str) -> str:
    """
    Normalize role names to official catalog names.
    Placeholder - could be expanded with full role catalog mapping.
    """
    if not role:
        return role
    
    # Common abbreviations and variations
    role_mapping = {
        "pl": "Projektledare",
        "pm": "Projektledare",
        "dev": "Utvecklare",
        "utvecklare": "Utvecklare",
        "systemutvecklare": "Systemutvecklare",
        "arkitekt": "Lösningsarkitekt",
        "testare": "Testledare",
        "test": "Testledare",
        "ux": "UX-designer",
        "ui": "UX-designer",
        "scrum master": "Scrum Master",
        "agile coach": "Agile Coach",
    }
    
    role_lower = role.lower().strip()
    return role_mapping.get(role_lower, role)


def validate_entities(entities: Dict) -> Dict:
    """
    Validate entities against business rules.
    Returns validation result with any issues found.
    """
    issues = []
    
    resources = entities.get('resources', [])
    
    # Check for KN5 rule
    has_level_5 = any(r.get('level') == 5 for r in resources)
    if has_level_5:
        issues.append({
            "rule": "KN5",
            "severity": "warning",
            "message": "Nivå 5-konsult kräver FKU (Förnyad Konkurrensutsättning)"
        })
    
    # Check for missing levels
    missing_levels = [r.get('role') for r in resources if r.get('level') is None]
    if missing_levels:
        issues.append({
            "rule": "MISSING_LEVEL",
            "severity": "info",
            "message": f"Nivå saknas för: {', '.join(missing_levels)}"
        })
    
    return {
        "valid": len([i for i in issues if i['severity'] == 'error']) == 0,
        "issues": issues
    }

