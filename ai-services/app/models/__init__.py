"""
Data Models for Adda Search Engine v5.5
Domain models, taxonomy enums, reasoning models, and avrop models for runtime.

v5.5 Changes:
- IntentTarget now includes search_strategy and search_terms
- SynthesizerResult added for response + entity changes
- Entity extraction moved from IntentAnalyzer to Synthesizer

v5.4 Changes:
- Added avrop.py with AvropsTyp, Resurs, AvropsData, RequiredFields
- Deprecated ResourceEntity, ExtractedEntities (use Resurs, AvropsData instead)
"""
from .domain import (
    # Taxonomy Enums
    TaxonomyRoot,
    TaxonomyBranch,
    ScopeContext,
    BlockType,
    VALID_BRANCHES,
    
    # Intent & Query Models
    IntentTarget,
    
    # Session State Models (DEPRECATED - use avrop.py models)
    ResourceEntity,
    ExtractedEntities,
    SessionState,
)

from .reasoning import (
    # Reasoning Models (Planner output)
    ReasoningPlan,
    ReasoningContext,
)

from .avrop import (
    # Avrop Models (v5.4)
    AvropsTyp,
    Region,
    Prismodell,
    Utvarderingsmodell,
    Resurs,
    AvropsData,
    AvropsProgress,
    REQUIRED_FIELDS,
    EntityAction,
    EntityChange,
    merge_avrop_data,
)

__all__ = [
    # Taxonomy
    "TaxonomyRoot",
    "TaxonomyBranch", 
    "ScopeContext",
    "BlockType",
    "VALID_BRANCHES",
    # Intent
    "IntentTarget",
    # Session State (DEPRECATED)
    "ResourceEntity",
    "ExtractedEntities",
    "SessionState",
    # Reasoning
    "ReasoningPlan",
    "ReasoningContext",
    # Avrop (v5.4)
    "AvropsTyp",
    "Region",
    "Prismodell",
    "Utvarderingsmodell",
    "Resurs",
    "AvropsData",
    "AvropsProgress",
    "REQUIRED_FIELDS",
    "EntityAction",
    "EntityChange",
    "merge_avrop_data",
]

