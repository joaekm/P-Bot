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
                    data = change.get('data', {})
                    if data:
                        success = False
                        for field, value in data.items():
                            if self._update_resource(result, resource_id, field, value):
                                success = True
                        if success:
                            applied_count += 1
                        else:
                            skipped_count += 1
                    else:
                        logger.warning(f"UPDATE resource missing 'data': {change}")
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
            
        # Allow behovsbeskrivning even if it's not in the strict validation set yet
        # (It should be added to valid_global_fields when reloading taxonomy, 
        # but to be safe for hot-reloads/partial updates)
        if field == 'behovsbeskrivning':
            avrop[field] = str(value) if value else None
            logger.info(f"Updated global: {field}={value}")
            return True

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
        Calculate completion progress for avrop based on current step requirements.
        
        Requirements per step (from assistant_prompts.yaml):
        - step_1_needs: Resources, Location/Anbudsomrade, Description
        - step_2_level: Level for all resources
        - step_3_volume: Volume/Budget, Dates
        - step_4_strategy: Pricing model, Evaluation criteria
        """
        # Determine active phase based on what is filled
        # For simple progress bar calculation, we stick to general completeness
        required_global = ['resources', 'volume', 'start_date', 'prismodell']
        
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
            'constraint_violations': []
        }

    def check_step_requirements(self, avrop: Dict, current_step: str) -> Dict:
        """
        Check if requirements for advancing FROM current_step are met.
        
        Returns:
            {
                'can_advance': bool,
                'missing': List[str],
                'next_step': str (suggestion)
            }
        """
        # Map step names (both legacy and new) to canonical internal names
        step_map = {
            'step_1_intake': 'step_1_intake',
            'step_1_needs': 'step_1_intake',
            'step_2_level': 'step_2_level',
            'step_3_volume': 'step_3_volume',
            'step_4_strategy': 'step_4_strategy'
        }
        
        step = step_map.get(current_step, 'step_1_intake')
        missing = []
        
        if step == 'step_1_intake':
            # Requirements to go to Step 2
            if not avrop.get('resources') or len(avrop.get('resources')) == 0:
                missing.append('minst en resurs (roll)')
            
            if not avrop.get('location_text') and not avrop.get('anbudsomrade'):
                missing.append('plats eller anbudsområde')
                
            # Note: behovsbeskrivning check is qualitative (LLM), 
            # here we only check if it exists if we strictly require it.
            # For now, we trust the LLM/Planner to hold back if description is poor.
            
            return {
                'can_advance': len(missing) == 0,
                'missing': missing,
                'next_step': 'step_2_level'
            }
            
        elif step == 'step_2_level':
            # Requirements to go to Step 3
            # All resources must have a level
            incomplete = [r.get('roll', 'okänd') for r in avrop.get('resources', []) if not r.get('level')]
            if incomplete:
                missing.append(f"kompetensnivå för {', '.join(incomplete)}")
                
            return {
                'can_advance': len(missing) == 0,
                'missing': missing,
                'next_step': 'step_3_volume'
            }
            
        elif step == 'step_3_volume':
            # Requirements to go to Step 4
            # Either Volume+Takpris OR Budget (Takpris used as budget holder if fastpris)
            has_volume = bool(avrop.get('volume'))
            has_money = bool(avrop.get('takpris'))
            
            if not (has_volume or has_money):
                missing.append('volym (timmar) eller budget')
                
            if not avrop.get('start_date'):
                missing.append('startdatum')
                
            if not avrop.get('end_date'):
                missing.append('slutdatum')
                
            return {
                'can_advance': len(missing) == 0,
                'missing': missing,
                'next_step': 'step_4_strategy'
            }
            
        elif step == 'step_4_strategy':
            # Requirements to finish
            if not avrop.get('prismodell'):
                missing.append('prismodell')
                
            return {
                'can_advance': len(missing) == 0,
                'missing': missing,
                'next_step': 'complete'
            }
            
        return {'can_advance': True, 'missing': [], 'next_step': 'general'}
    
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
            'behovsbeskrivning': None,
            'uppdragsbeskrivning': None,
            'resultatbeskrivning': None,
            'godkannandevillkor': None,
            'hanterar_personuppgifter': None,
            'sakerhetsklassad': None
        }


