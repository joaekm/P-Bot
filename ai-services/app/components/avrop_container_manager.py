"""
AvropsContainerManager v5.24 - Deterministisk hantering av avrop-data (varukorg)

Placering i pipeline:
    IntentAnalyzer → ContextBuilder → Planner → [AvropsContainerManager] → Synthesizer
                                         ↓                ↓
                                  entity_changes    updated_avrop

IN:  avrop: dict, changes: list (från Planner)
OUT: dict (uppdaterad avrop)

Ansvar:
- Applicera entity_changes (ADD/UPDATE/DELETE) på avrop
- Validera fältnamn mot taxonomin (SSOT)
- Logga state varje körning
- INGEN LLM - helt deterministisk

Fältnamn (från adda_taxonomy.json):
- Global: resources, region, location_text, anbudsomrade, volume, start_date, end_date,
         takpris, prismodell, pris_vikt, kvalitet_vikt, avrop_typ, uppdragsbeskrivning,
         resultatbeskrivning, godkannandevillkor, hanterar_personuppgifter, sakerhetsklassad
- Resurs: id, roll, level, antal, kompetensomrade, is_complete
"""
import json
import logging
import uuid
from pathlib import Path
from typing import Dict, List, Any, Optional
from copy import deepcopy

logger = logging.getLogger("ADDA_ENGINE")


class AvropsContainerManager:
    """
    Deterministisk komponent för att hantera avrop-data.
    Läser taxonomin för fältvalidering.
    """
    
    def __init__(self, taxonomy_path: Optional[Path] = None):
        """
        Initialize with taxonomy for field validation.
        
        Args:
            taxonomy_path: Path to adda_taxonomy.json
        """
        self.taxonomy = self._load_taxonomy(taxonomy_path)
        self.valid_global_fields = set(self.taxonomy.get('avrop_fields', {}).get('global', {}).keys())
        self.valid_resurs_fields = set(self.taxonomy.get('avrop_fields', {}).get('resurs', {}).keys())
        
        logger.info(f"AvropsContainerManager initialized with {len(self.valid_global_fields)} global fields, "
                   f"{len(self.valid_resurs_fields)} resurs fields")
    
    def _load_taxonomy(self, taxonomy_path: Optional[Path]) -> Dict:
        """Load taxonomy from file."""
        if taxonomy_path is None:
            # Default path relative to this file
            base_dir = Path(__file__).resolve().parent.parent.parent
            taxonomy_path = base_dir / "storage" / "index" / "adda_taxonomy.json"
        
        try:
            with open(taxonomy_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load taxonomy: {e}")
            return {}
    
    def apply(self, avrop: Dict, changes: List[Dict]) -> Dict:
        """
        Apply entity changes to avrop.
        
        Args:
            avrop: Current avrop dict (shopping cart)
            changes: List of changes from Planner:
                [
                    {"action": "ADD", "type": "resource", "data": {"roll": "X", "level": 4}},
                    {"action": "UPDATE", "type": "global", "field": "location_text", "value": "Y"},
                    {"action": "DELETE", "type": "resource", "id": "res_1"}
                ]
        
        Returns:
            Updated avrop dict
        """
        # Deep copy to avoid mutation
        result = deepcopy(avrop)
        
        # Ensure resources list exists
        if 'resources' not in result:
            result['resources'] = []
        
        applied_count = 0
        skipped_count = 0
        
        for change in changes:
            action = change.get('action', '').upper()
            change_type = change.get('type', '').lower()
            
            try:
                if action == 'ADD' and change_type == 'resource':
                    self._add_resource(result, change.get('data', {}))
                    applied_count += 1
                    
                elif action == 'UPDATE' and change_type == 'global':
                    field = change.get('field')
                    value = change.get('value')
                    if self._update_global(result, field, value):
                        applied_count += 1
                    else:
                        skipped_count += 1
                        
                elif action == 'UPDATE' and change_type == 'resource':
                    resource_id = change.get('id')
                    field = change.get('field')
                    value = change.get('value')
                    if self._update_resource(result, resource_id, field, value):
                        applied_count += 1
                    else:
                        skipped_count += 1
                        
                elif action == 'DELETE' and change_type == 'resource':
                    resource_id = change.get('id')
                    if self._remove_resource(result, resource_id):
                        applied_count += 1
                    else:
                        skipped_count += 1
                else:
                    logger.warning(f"Unknown change: action={action}, type={change_type}")
                    skipped_count += 1
                    
            except Exception as e:
                logger.error(f"Error applying change {change}: {e}")
                skipped_count += 1
        
        # Log state
        self._log_state(result, applied_count, skipped_count)
        
        return result
    
    def _add_resource(self, avrop: Dict, data: Dict) -> None:
        """Add a new resource to avrop."""
        # Generate ID if not provided
        resource_id = data.get('id') or f"res_{uuid.uuid4().hex[:8]}"
        
        # Build resource with validated fields
        resource = {'id': resource_id}
        
        for field, value in data.items():
            if field in self.valid_resurs_fields:
                resource[field] = self._parse_value(field, value)
            else:
                logger.warning(f"Invalid resurs field '{field}' - skipping")
        
        # Set defaults
        resource.setdefault('antal', 1)
        resource['is_complete'] = self._is_resource_complete(resource)
        
        avrop['resources'].append(resource)
        logger.info(f"Added resource: {resource.get('roll', 'Unknown')} (id={resource_id})")
    
    def _update_global(self, avrop: Dict, field: str, value: Any) -> bool:
        """Update a global field on avrop."""
        if not field:
            logger.warning("No field specified for global update")
            return False
            
        if field not in self.valid_global_fields:
            logger.warning(f"Invalid global field '{field}' - skipping")
            return False
        
        parsed_value = self._parse_value(field, value)
        avrop[field] = parsed_value
        logger.info(f"Updated global: {field}={parsed_value}")
        return True
    
    def _update_resource(self, avrop: Dict, resource_id: str, field: str, value: Any) -> bool:
        """Update a field on an existing resource."""
        if not resource_id:
            logger.warning("No resource_id specified for resource update")
            return False
            
        if field and field not in self.valid_resurs_fields:
            logger.warning(f"Invalid resurs field '{field}' - skipping")
            return False
        
        for resource in avrop.get('resources', []):
            if resource.get('id') == resource_id:
                if field:
                    resource[field] = self._parse_value(field, value)
                    resource['is_complete'] = self._is_resource_complete(resource)
                    logger.info(f"Updated resource {resource_id}: {field}={value}")
                return True
        
        logger.warning(f"Resource {resource_id} not found")
        return False
    
    def _remove_resource(self, avrop: Dict, resource_id: str) -> bool:
        """Remove a resource from avrop."""
        if not resource_id:
            logger.warning("No resource_id specified for deletion")
            return False
        
        original_count = len(avrop.get('resources', []))
        avrop['resources'] = [r for r in avrop.get('resources', []) if r.get('id') != resource_id]
        
        if len(avrop['resources']) < original_count:
            logger.info(f"Removed resource: {resource_id}")
            return True
        else:
            logger.warning(f"Resource {resource_id} not found for deletion")
            return False
    
    def _parse_value(self, field: str, value: Any) -> Any:
        """Parse and clean value based on field type."""
        if value is None:
            return None
        
        # Integer fields
        int_fields = {'volume', 'takpris', 'pris_vikt', 'kvalitet_vikt', 'level', 'antal'}
        if field in int_fields:
            if isinstance(value, int):
                return value
            if isinstance(value, str):
                # Extract digits only (e.g., "1800000 SEK" -> 1800000)
                digits = ''.join(c for c in value if c.isdigit())
                return int(digits) if digits else None
            return None
        
        # Boolean fields
        bool_fields = {'hanterar_personuppgifter', 'sakerhetsklassad', 'is_complete'}
        if field in bool_fields:
            if isinstance(value, bool):
                return value
            if isinstance(value, str):
                return value.lower() in ('true', 'ja', 'yes', '1')
            return bool(value)
        
        # String fields - just return as-is
        return str(value) if value else None
    
    def _is_resource_complete(self, resource: Dict) -> bool:
        """Check if a resource has all required fields."""
        required = ['roll', 'level']
        return all(resource.get(f) for f in required)
    
    def _log_state(self, avrop: Dict, applied: int, skipped: int) -> None:
        """Log current avrop state."""
        resource_summary = []
        for r in avrop.get('resources', []):
            resource_summary.append(f"{r.get('roll', '?')}(L{r.get('level', '?')})")
        
        logger.info(
            f"📦 AvropsContainer State: "
            f"{len(avrop.get('resources', []))} resources [{', '.join(resource_summary)}], "
            f"region={avrop.get('region', '-')}, "
            f"location={avrop.get('location_text', '-')}, "
            f"volume={avrop.get('volume', '-')}, "
            f"changes: {applied} applied, {skipped} skipped"
        )
    
    def calculate_progress(self, avrop: Dict) -> Dict:
        """
        Calculate completion progress for avrop.
        
        Returns:
            Dict with completion_percent, is_complete, missing_fields
        """
        required_global = ['resources', 'volume', 'start_date']
        optional_global = ['location_text', 'region', 'end_date', 'takpris', 'prismodell']
        
        missing = []
        filled = 0
        total = len(required_global)
        
        for field in required_global:
            value = avrop.get(field)
            if field == 'resources':
                if value and len(value) > 0:
                    filled += 1
                else:
                    missing.append('resources')
            elif value:
                filled += 1
            else:
                missing.append(field)
        
        # Check resource completeness
        incomplete_resources = []
        for r in avrop.get('resources', []):
            if not r.get('is_complete', False):
                incomplete_resources.append(r.get('roll', r.get('id', 'unknown')))
        
        if incomplete_resources:
            missing.append(f"level för: {', '.join(incomplete_resources)}")
        
        completion_percent = int((filled / total) * 100) if total > 0 else 0
        
        return {
            'completion_percent': completion_percent,
            'is_complete': len(missing) == 0 and len(incomplete_resources) == 0,
            'missing_fields': missing,
            'constraint_violations': []  # Could add validation here
        }
    
    def create_empty_avrop(self) -> Dict:
        """Create an empty avrop dict with proper structure."""
        return {
            'resources': [],
            'region': None,
            'location_text': None,
            'anbudsomrade': None,
            'volume': None,
            'start_date': None,
            'end_date': None,
            'takpris': None,
            'prismodell': None,
            'pris_vikt': None,
            'kvalitet_vikt': None,
            'avrop_typ': None,
            'uppdragsbeskrivning': None,
            'resultatbeskrivning': None,
            'godkannandevillkor': None,
            'hanterar_personuppgifter': None,
            'sakerhetsklassad': None
        }


