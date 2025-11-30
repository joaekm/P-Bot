"""
Adda P-Bot Domain Models v2
Runtime contract for ai-services - COPIED from data_pipeline (not imported).
This ensures ai-services can run independently of data_pipeline.
"""
from enum import Enum
from pydantic import BaseModel, Field
from typing import List, Literal, Optional


# =============================================================================
# TAXONOMY ENUMS (Copied from data_pipeline/models.py)
# =============================================================================

class TaxonomyRoot(str, Enum):
    """Top-level taxonomy categories."""
    DOMAIN_OBJECTS = "DOMAIN_OBJECTS"       # Det fysiska/konkreta (roller, dokument, platser)
    BUSINESS_CONCEPTS = "BUSINESS_CONCEPTS" # Det abstrakta/logiska (pris, regler, strategi)
    PROCESS = "PROCESS"                     # Tiden/Flödet (faser, steg)


class TaxonomyBranch(str, Enum):
    """Branch categories under each root."""
    # Under DOMAIN_OBJECTS
    ROLES = "ROLES"             # Roller, Kompetens, Nivåer
    ARTIFACTS = "ARTIFACTS"     # CV, Avtal, Bilagor, Dokument
    LOCATIONS = "LOCATIONS"     # Regioner, Geografi, Plats
    
    # Under BUSINESS_CONCEPTS
    FINANCIALS = "FINANCIALS"   # Pris, Volym, Budget, Optioner
    GOVERNANCE = "GOVERNANCE"   # Lagar, Regler, Säkerhet, GDPR, Compliance
    STRATEGY = "STRATEGY"       # Affärsregler, Avropsformer (FKU/DR), Metod
    
    # Under PROCESS
    PHASES = "PHASES"           # Intake, Evaluation, Contract, Management


class ScopeContext(str, Enum):
    """
    Scope Context - The "Gift vs Medicine" logic.
    Determines how the content should be treated in search/retrieval.
    """
    FRAMEWORK_SPECIFIC = "FRAMEWORK_SPECIFIC"  # Adda-specifikt (Trumfar allt)
    GENERAL_LEGAL = "GENERAL_LEGAL"            # UHM/Lag (Fallback)
    DOMAIN_KNOWLEDGE = "DOMAIN_KNOWLEDGE"      # Allmänt vetande


class BlockType(str, Enum):
    """Block type classification."""
    RULE = "RULE"                   # Tvingande regler: SKA, MÅSTE, FÅR EJ
    DEFINITION = "DEFINITION"       # Fakta, begreppsförklaringar
    INSTRUCTION = "INSTRUCTION"     # Steg-för-steg processer
    DATA_POINTER = "DATA_POINTER"   # Referens till extern data
    EXAMPLE = "EXAMPLE"             # Exempel/Case studies


# Valid branch mappings per root (for validation)
VALID_BRANCHES = {
    TaxonomyRoot.DOMAIN_OBJECTS: [
        TaxonomyBranch.ROLES, 
        TaxonomyBranch.ARTIFACTS, 
        TaxonomyBranch.LOCATIONS
    ],
    TaxonomyRoot.BUSINESS_CONCEPTS: [
        TaxonomyBranch.FINANCIALS, 
        TaxonomyBranch.GOVERNANCE, 
        TaxonomyBranch.STRATEGY
    ],
    TaxonomyRoot.PROCESS: [
        TaxonomyBranch.PHASES
    ],
}


# =============================================================================
# INTENT TARGET MODEL (Query -> Taxonomy Mapping)
# =============================================================================

class IntentTarget(BaseModel):
    """
    Result of Intent Analysis - maps a user query to taxonomy coordinates.
    Used by ContextBuilder to fetch relevant documents.
    """
    original_query: str = Field(..., description="The original user query")
    
    # Taxonomy Coordinates
    taxonomy_roots: List[TaxonomyRoot] = Field(
        default_factory=list,
        description="Detected root categories (usually 1-2)"
    )
    taxonomy_branches: List[TaxonomyBranch] = Field(
        default_factory=list,
        description="Detected branch categories (usually 1-3)"
    )
    
    # Harvested Concepts
    detected_topics: List[str] = Field(
        default_factory=list,
        description="Topics found in query that match vocabulary (e.g., 'Takpris', 'Kompetensnivå')"
    )
    detected_entities: List[str] = Field(
        default_factory=list,
        description="Named entities found in query (e.g., 'Nivå 4', 'Stockholm')"
    )
    
    # Search Preferences
    scope_preference: List[ScopeContext] = Field(
        default_factory=lambda: [ScopeContext.FRAMEWORK_SPECIFIC],
        description="Preferred scope contexts for search (ordered by priority)"
    )
    
    # Intent Classification
    intent_category: Literal["FACT", "INSPIRATION", "INSTRUCTION"] = Field(
        default="FACT",
        description="Query intent: FACT (rules/prices), INSPIRATION (examples), INSTRUCTION (how-to)"
    )
    
    # Confidence
    confidence: float = Field(
        default=0.5,
        ge=0.0, le=1.0,
        description="Confidence score for the classification"
    )
    
    def get_scope_filter(self) -> List[str]:
        """Get scope values for ChromaDB filter."""
        return [s.value for s in self.scope_preference]
    
    def get_branch_filter(self) -> Optional[str]:
        """Get primary branch for ChromaDB filter."""
        if self.taxonomy_branches:
            return self.taxonomy_branches[0].value
        return None
    
    def should_block_secondary(self) -> bool:
        """Determine if SECONDARY sources should be blocked (Ghost Mode)."""
        return self.intent_category == "FACT"


# =============================================================================
# SESSION STATE MODELS (Extracted from conversation)
# =============================================================================

class ResourceEntity(BaseModel):
    """A resource (person/role) being procured."""
    id: str = Field(default="", description="Unique identifier")
    role: str = Field(default="", description="Role name (e.g., 'Projektledare')")
    level: Optional[str] = Field(default=None, description="Competence level (1-4)")
    quantity: int = Field(default=1, description="Number of resources")
    status: str = Field(default="PENDING", description="PENDING, DONE, LOCKED")
    dialog_status: str = Field(default="ACTIVE", description="UNTOUCHED, ACTIVE, PARKED, LOCKED")


class ExtractedEntities(BaseModel):
    """Entities extracted from conversation."""
    resources: List[ResourceEntity] = Field(default_factory=list)
    location: Optional[str] = Field(default=None, description="Geographic location")
    volume: Optional[str] = Field(default=None, description="Volume in hours")
    start_date: Optional[str] = Field(default=None, description="Start date")
    price_cap: Optional[str] = Field(default=None, description="Price cap")


class SessionState(BaseModel):
    """Complete session state from extraction."""
    extracted_entities: ExtractedEntities = Field(default_factory=ExtractedEntities)
    missing_info: List[str] = Field(default_factory=list)
    current_intent: Literal["FACT", "INSPIRATION", "INSTRUCTION"] = Field(default="INSPIRATION")
    confidence: float = Field(default=0.0)
    forced_strategy: Optional[str] = Field(default=None, description="Strategy forced by validator")

