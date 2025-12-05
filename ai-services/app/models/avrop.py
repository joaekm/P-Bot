"""
Avrop Data Models (v5.5)
Defines the data structures for procurement requests (avrop).

This module replaces the old ResourceEntity and ExtractedEntities models
with a more comprehensive structure based on the Avropsvägledningen.

Key changes from v5.4:
- Added anbudsomrade field for full region display (e.g., "B - Mellersta Norrland")
- Fixed Region enum comments to match actual anbudsområden

Key changes from v5.3:
- AvropsTyp enum determines the procurement path (DR vs FKU)
- Resurs model without dialog_status (it didn't work)
- RequiredFields provides hardcoded validation per AvropsTyp
- AvropsProgress calculates completion percentage
"""
from enum import Enum
from pydantic import BaseModel, Field, field_validator
from typing import List, Optional, Literal, Dict, Any


# =============================================================================
# ENUMS
# =============================================================================

class AvropsTyp(str, Enum):
    """
    Type of procurement - determines which path to take.
    
    The system auto-detects this based on:
    - Volume > 320h → FKU
    - Level 5 → FKU
    - Custom role (not in 24 example roles) → FKU
    - Project (result responsibility) → FKU_PROJEKT
    """
    DR_RESURS = "DR_RESURS"           # Dynamisk Rangordning (snabbspåret)
    FKU_RESURS = "FKU_RESURS"         # Förnyad Konkurrensutsättning - Resurs
    FKU_PROJEKT = "FKU_PROJEKT"       # Förnyad Konkurrensutsättning - Projekt


class Region(str, Enum):
    """Geographic regions (Anbudsområden) A-G."""
    A = "A"  # Norra Norrland (Norrbotten, Västerbotten)
    B = "B"  # Mellersta Norrland (Jämtland, Västernorrland)
    C = "C"  # Norra Mellansverige (Gävleborg, Dalarna, Värmland, Örebro, Västmanland, Södermanland)
    D = "D"  # Stockholm (Stockholm, Uppsala, Gotland)
    E = "E"  # Västsverige (Västra Götaland, Halland)
    F = "F"  # Småland/Östergötland (Östergötland, Jönköping, Kalmar)
    G = "G"  # Sydsverige (Skåne, Blekinge, Kronoberg)


class Prismodell(str, Enum):
    """Pricing models for FKU."""
    LOPANDE = "LOPANDE"           # Löpande räkning
    FAST_PRIS = "FAST_PRIS"       # Fast pris
    LOPANDE_MED_TAK = "LOPANDE_MED_TAK"  # Löpande med takpris


class Utvarderingsmodell(str, Enum):
    """Evaluation models for FKU."""
    PRIS_100 = "PRIS_100"         # 100% pris
    PRIS_70_KVALITET_30 = "PRIS_70_KVALITET_30"  # 70% pris, 30% kvalitet
    PRIS_50_KVALITET_50 = "PRIS_50_KVALITET_50"  # 50% pris, 50% kvalitet


# =============================================================================
# RESURS MODEL (replaces ResourceEntity)
# =============================================================================

class Resurs(BaseModel):
    """
    A resource (consultant role) being procured.
    
    Note: dialog_status has been removed - it didn't work as intended.
    Instead, we track completion via RequiredFields validation.
    """
    id: str = Field(default="", description="Unique identifier (e.g., 'res_1')")
    roll: str = Field(..., description="Role name (e.g., 'Projektledare')")
    level: Optional[int] = Field(default=None, ge=1, le=5, description="Competence level 1-5")
    antal: int = Field(default=1, ge=1, description="Number of resources with this role")
    kompetensomrade: Optional[str] = Field(default=None, description="Competence area (for DR)")
    
    # Computed field
    is_complete: bool = Field(default=False, description="True if roll AND level are set")
    
    @field_validator('level', mode='before')
    @classmethod
    def clamp_level(cls, v):
        """Clamp level to 1-5 range."""
        if v is None:
            return None
        try:
            level = int(v)
            return max(1, min(5, level))
        except (ValueError, TypeError):
            return None
    
    def model_post_init(self, __context):
        """Calculate is_complete after initialization."""
        object.__setattr__(self, 'is_complete', bool(self.roll and self.level is not None))
    
    def to_display(self) -> str:
        """Human-readable representation."""
        level_str = f"Nivå {self.level}" if self.level else "Nivå ej angiven"
        antal_str = f"{self.antal} st" if (self.antal or 0) > 1 else ""
        return f"{self.roll} ({level_str}) {antal_str}".strip()


# =============================================================================
# AVROP DATA MODEL (the "shopping cart")
# =============================================================================

class AvropsData(BaseModel):
    """
    Complete data for a procurement request (avrop).
    
    This is the "shopping cart" that accumulates data during conversation.
    The resources list must contain at least one resource for a valid avrop.
    """
    # Type (auto-detected or manually set)
    avrop_typ: Optional[AvropsTyp] = Field(
        default=None, 
        description="Procurement type - auto-detected based on rules"
    )
    
    # Resources (list, must have at least 1)
    resources: List[Resurs] = Field(
        default_factory=list,
        description="List of resources being procured (min 1 required)"
    )
    
    # Time & Volume
    start_date: Optional[str] = Field(default=None, description="Start date (YYYY-MM-DD)")
    end_date: Optional[str] = Field(default=None, description="End date (YYYY-MM-DD)")
    volume: Optional[int] = Field(default=None, ge=0, description="Total hours")
    
    # Location
    region: Optional[Region] = Field(default=None, description="Geographic region A-G")
    location_text: Optional[str] = Field(default=None, description="Free text location (e.g., 'Stockholm')")
    anbudsomrade: Optional[str] = Field(default=None, description="Full anbudsområde string (e.g., 'B - Mellersta Norrland')")
    
    # Pricing (for FKU)
    prismodell: Optional[Prismodell] = Field(default=None, description="Pricing model")
    takpris: Optional[int] = Field(default=None, description="Price cap per hour (kr)")
    
    # Evaluation (for FKU)
    utvarderingsmodell: Optional[Utvarderingsmodell] = Field(default=None)
    
    # Descriptions (for FKU)
    uppdragsbeskrivning: Optional[str] = Field(default=None, description="Assignment description")
    resultatbeskrivning: Optional[str] = Field(default=None, description="Result description (FKU_PROJEKT)")
    godkannandevillkor: Optional[str] = Field(default=None, description="Acceptance criteria (FKU_PROJEKT)")
    
    # Flags
    hanterar_personuppgifter: Optional[bool] = Field(default=None, description="Handles personal data?")
    sakerhetsklassad: Optional[bool] = Field(default=None, description="Security classified?")
    
    def detect_avrop_typ(self) -> AvropsTyp:
        """
        Auto-detect the procurement type based on rules.
        
        Forces FKU if:
        - Volume > 320 hours
        - Any resource has level 5
        - (Future: custom role not in 24 example roles)
        """
        # Check volume
        if self.volume and self.volume > 320:
            return AvropsTyp.FKU_RESURS
        
        # Check for level 5
        for res in self.resources:
            if res.level == 5:
                return AvropsTyp.FKU_RESURS
        
        # Default to DR
        return AvropsTyp.DR_RESURS
    
    def get_resource_by_id(self, res_id: str) -> Optional[Resurs]:
        """Find a resource by ID."""
        for res in self.resources:
            if res.id == res_id:
                return res
        return None
    
    def get_resource_by_role(self, role: str) -> Optional[Resurs]:
        """Find a resource by role name (case-insensitive)."""
        role_lower = role.lower()
        for res in self.resources:
            if res.roll.lower() == role_lower:
                return res
        return None


# =============================================================================
# REQUIRED FIELDS (hardcoded validation)
# =============================================================================

# Define required fields per AvropsTyp
REQUIRED_FIELDS: Dict[AvropsTyp, Dict[str, Any]] = {
    AvropsTyp.DR_RESURS: {
        "global": ["start_date", "end_date", "volume", "region"],
        "per_resource": ["roll", "level", "kompetensomrade"],
        "constraints": {
            "volume_max": 320,
            "level_max": 4,
        }
    },
    AvropsTyp.FKU_RESURS: {
        "global": ["start_date", "end_date", "volume", "prismodell", "utvarderingsmodell"],
        "per_resource": ["roll", "level"],
        "constraints": {
            "level_max": 5,
        }
    },
    AvropsTyp.FKU_PROJEKT: {
        "global": ["resultatbeskrivning", "end_date", "godkannandevillkor", "prismodell"],
        "per_resource": [],  # No per-resource requirements for project
        "constraints": {}
    }
}


class AvropsProgress(BaseModel):
    """
    Calculates completion progress for an AvropsData.
    
    This replaces the LLM-generated missing_info with a deterministic calculation.
    """
    avrop_typ: AvropsTyp
    total_fields: int = Field(default=0)
    completed_fields: int = Field(default=0)
    missing_fields: List[str] = Field(default_factory=list)
    completion_percent: float = Field(default=0.0)
    is_complete: bool = Field(default=False)
    
    # Constraint violations
    constraint_violations: List[str] = Field(default_factory=list)
    
    @classmethod
    def calculate(cls, avrop: AvropsData) -> "AvropsProgress":
        """Calculate progress for an AvropsData object."""
        # Detect type if not set
        avrop_typ = avrop.avrop_typ or avrop.detect_avrop_typ()
        
        requirements = REQUIRED_FIELDS.get(avrop_typ, REQUIRED_FIELDS[AvropsTyp.DR_RESURS])
        
        missing = []
        violations = []
        total = 0
        completed = 0
        
        # Check resources list (must have at least 1)
        total += 1
        if avrop.resources:
            completed += 1
        else:
            missing.append("resources (minst 1 resurs krävs)")
        
        # Check global fields
        for field in requirements["global"]:
            total += 1
            value = getattr(avrop, field, None)
            if value is not None and value != "":
                completed += 1
            else:
                missing.append(field)
        
        # Check per-resource fields
        for i, res in enumerate(avrop.resources):
            for field in requirements["per_resource"]:
                total += 1
                value = getattr(res, field, None)
                if value is not None and value != "":
                    completed += 1
                else:
                    missing.append(f"{field} för {res.roll or f'resurs {i+1}'}")
        
        # Check constraints
        constraints = requirements.get("constraints", {})
        
        if "volume_max" in constraints and avrop.volume:
            if avrop.volume > constraints["volume_max"]:
                violations.append(f"Volym {avrop.volume}h överstiger {constraints['volume_max']}h för DR")
        
        if "level_max" in constraints:
            for res in avrop.resources:
                if res.level and res.level > constraints["level_max"]:
                    violations.append(f"Nivå {res.level} för {res.roll} överstiger max {constraints['level_max']} för {avrop_typ.value}")
        
        # Calculate percentage
        percent = (completed / total * 100) if total > 0 else 0
        
        return cls(
            avrop_typ=avrop_typ,
            total_fields=total,
            completed_fields=completed,
            missing_fields=missing,
            completion_percent=round(percent, 1),
            is_complete=(len(missing) == 0 and len(violations) == 0),
            constraint_violations=violations
        )


# =============================================================================
# ENTITY ACTIONS (for merge with DELETE support)
# =============================================================================

class EntityAction(str, Enum):
    """Actions that can be performed on entities during merge."""
    ADD = "ADD"
    UPDATE = "UPDATE"
    DELETE = "DELETE"


class EntityChange(BaseModel):
    """
    Represents a change to be applied to AvropsData.
    
    Used by IntentAnalyzer to communicate changes to Engine.
    """
    action: EntityAction
    target_type: Literal["resource", "global"] = "resource"
    target_id: Optional[str] = Field(default=None, description="Resource ID for resource changes")
    target_field: Optional[str] = Field(default=None, description="Field name for global changes")
    new_value: Optional[Any] = Field(default=None, description="New value (for ADD/UPDATE)")
    
    # For ADD resource
    new_resource: Optional[Resurs] = Field(default=None, description="New resource to add")


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def merge_avrop_data(old: AvropsData, changes: List[EntityChange]) -> AvropsData:
    """
    Apply a list of changes to AvropsData.
    
    Supports ADD, UPDATE, and DELETE operations.
    """
    # Create a copy
    new_data = old.model_copy(deep=True)
    
    for change in changes:
        if change.action == EntityAction.DELETE:
            if change.target_type == "resource" and change.target_id:
                # Remove resource by ID
                new_data.resources = [r for r in new_data.resources if r.id != change.target_id]
            elif change.target_type == "resource" and change.target_field:
                # Remove resource by role name
                role_lower = change.target_field.lower()
                new_data.resources = [r for r in new_data.resources if r.roll.lower() != role_lower]
        
        elif change.action == EntityAction.ADD:
            if change.target_type == "resource" and change.new_resource:
                # Add new resource
                new_data.resources.append(change.new_resource)
            elif change.target_type == "global" and change.target_field:
                # Set global field
                setattr(new_data, change.target_field, change.new_value)
        
        elif change.action == EntityAction.UPDATE:
            if change.target_type == "resource" and change.target_id:
                # Update existing resource
                for res in new_data.resources:
                    if res.id == change.target_id:
                        if change.target_field and change.new_value is not None:
                            setattr(res, change.target_field, change.new_value)
                        break
            elif change.target_type == "global" and change.target_field:
                # Update global field
                setattr(new_data, change.target_field, change.new_value)
    
    # Re-detect avrop_typ after changes
    new_data.avrop_typ = new_data.detect_avrop_typ()
    
    return new_data

