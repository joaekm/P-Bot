"""
Adda P-Bot Data Pipeline Models v2
Strict typing with Enums and Pydantic for Scope-Aware Taxonomy.
"""
from enum import Enum
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Literal
import uuid as uuid_lib


# =============================================================================
# TAXONOMY ENUMS (Discovered via taxonomy_discovery_v2.py)
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


# =============================================================================
# PYDANTIC MODELS
# =============================================================================

class ConstraintRule(BaseModel):
    """
    A constraint rule for validation.
    Used by the Validator component to check extracted entities.
    """
    param: str = Field(..., description="Parameter to constrain: volume_hours, competence_level, location, etc.")
    operator: str = Field(..., description="Operator: MAX, MIN, EQUALS, ONE_OF, GT, NOT_IN")
    value: Any = Field(..., description="Threshold value or list of valid values")
    unit: str | None = Field(default=None, description="Unit: hours, months, sek, level")
    action: str = Field(default="WARN", description="Action: BLOCK, WARN, TRIGGER_STRATEGY_FKU")
    error_msg: str = Field(default="", description="User-friendly error message in Swedish")


class GraphRelation(BaseModel):
    """A relation to another node in the knowledge graph."""
    type: str = Field(..., description="Relation type: TRIGGERS, REQUIRES, BLOCKS, REFERENCES")
    target: str = Field(..., description="Target node identifier")


class SmartBlockMetadata(BaseModel):
    """
    Metadata for a Smart Block.
    Contains all classification and harvesting data.
    """
    # Core Classification
    block_type: BlockType = Field(default=BlockType.DEFINITION)
    taxonomy_root: TaxonomyRoot = Field(default=TaxonomyRoot.DOMAIN_OBJECTS)
    taxonomy_branch: TaxonomyBranch = Field(default=TaxonomyBranch.ROLES)
    scope_context: ScopeContext = Field(default=ScopeContext.FRAMEWORK_SPECIFIC)
    
    # Harvesting (Bottom-Up Discovery)
    topic_tags: List[str] = Field(
        default_factory=list,
        description="Renodlade begrepp, INGA värden (t.ex. 'Timpris', inte '1200kr')"
    )
    entities: List[str] = Field(
        default_factory=list,
        description="Namngivna objekt (t.ex. 'Nivå 4', 'Bilaga 1', '320-timmarsregeln')"
    )
    
    # Legacy tags (for Obsidian compatibility)
    tags: List[str] = Field(default_factory=list)
    
    # Navigation
    suggested_phase: List[str] = Field(
        default_factory=lambda: ["general"],
        description="Process phases: step_1_intake, step_2_level, step_3_volume, step_4_strategy"
    )
    
    # Validation Rules
    constraints: List[Dict[str, Any]] = Field(default_factory=list)
    
    # Graph Relations
    graph_relations: List[Dict[str, str]] = Field(default_factory=list)
    
    def validate_branch_root_combo(self) -> bool:
        """Check if branch is valid for the given root."""
        valid = VALID_BRANCHES.get(self.taxonomy_root, [])
        return self.taxonomy_branch in valid


class SmartBlock(BaseModel):
    """
    A Smart Block - the atomic unit of knowledge in the Lake.
    """
    uuid: str = Field(default_factory=lambda: str(uuid_lib.uuid4()))
    doc_type: str = "smart_block"
    source_file: str = Field(..., description="Original filename")
    authority_level: Literal["PRIMARY", "SECONDARY"] = Field(
        ..., 
        description="Zone: PRIMARY (Adda rules) or SECONDARY (UHM/General)"
    )
    content_markdown: str = Field(..., description="The actual content in Markdown format")
    metadata: SmartBlockMetadata = Field(default_factory=SmartBlockMetadata)
    
    def to_yaml_frontmatter(self) -> str:
        """Generate YAML frontmatter string for Markdown file."""
        import yaml
        
        data = {
            "uuid": self.uuid,
            "doc_type": self.doc_type,
            "source_file": self.source_file,
            "authority_level": self.authority_level,
            "block_type": self.metadata.block_type.value,
            "taxonomy_root": self.metadata.taxonomy_root.value,
            "taxonomy_branch": self.metadata.taxonomy_branch.value,
            "scope_context": self.metadata.scope_context.value,
            "suggested_phase": self.metadata.suggested_phase,
            "topic_tags": self.metadata.topic_tags,
            "entities": self.metadata.entities,
            "tags": self.metadata.tags,
        }
        
        if self.metadata.constraints:
            data["constraints"] = self.metadata.constraints
        if self.metadata.graph_relations:
            data["graph_relations"] = self.metadata.graph_relations
        
        return f"---\n{yaml.safe_dump(data, allow_unicode=True, default_flow_style=False, sort_keys=False)}---"
    
    def to_markdown_file(self) -> str:
        """Generate complete Markdown file content with frontmatter."""
        return f"{self.to_yaml_frontmatter()}\n\n{self.content_markdown}"
    
    def generate_filename(self) -> str:
        """Generate a filename based on metadata."""
        phase = self.metadata.suggested_phase[0] if self.metadata.suggested_phase else "general"
        phase_short = phase.replace("step_", "") if phase.startswith("step_") else phase
        block_type = self.metadata.block_type.value
        zone = self.authority_level.upper()
        short_uuid = self.uuid[:8]
        
        return f"{phase_short}_{block_type}_{zone}_{short_uuid}.md"


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def parse_llm_response_to_block(
    llm_data: Dict[str, Any],
    source_file: str,
    authority_level: Literal["PRIMARY", "SECONDARY"]
) -> SmartBlock | None:
    """
    Parse LLM JSON response into a validated SmartBlock.
    Returns None if validation fails.
    """
    try:
        content = llm_data.get("content_markdown", "")
        if not content or not content.strip():
            return None
        
        meta_raw = llm_data.get("metadata", {})
        
        # Map old field names to new ones
        metadata = SmartBlockMetadata(
            block_type=BlockType(meta_raw.get("block_type", "DEFINITION")),
            taxonomy_root=TaxonomyRoot(meta_raw.get("taxonomy_root", "DOMAIN_OBJECTS")),
            taxonomy_branch=TaxonomyBranch(meta_raw.get("taxonomy_branch", "ROLES")),
            scope_context=ScopeContext(meta_raw.get("scope_context", "FRAMEWORK_SPECIFIC")),
            topic_tags=meta_raw.get("topic_tags", []),
            entities=meta_raw.get("entities", []),
            tags=meta_raw.get("tags", []),
            suggested_phase=meta_raw.get("suggested_phase", meta_raw.get("process_step", ["general"])),
            constraints=meta_raw.get("constraints", []),
            graph_relations=meta_raw.get("graph_relations", [])
        )
        
        # Validate branch-root combo
        if not metadata.validate_branch_root_combo():
            # Auto-correct: Use first valid branch for this root
            valid_branches = VALID_BRANCHES.get(metadata.taxonomy_root, [])
            if valid_branches:
                metadata.taxonomy_branch = valid_branches[0]
        
        return SmartBlock(
            source_file=source_file,
            authority_level=authority_level,
            content_markdown=content,
            metadata=metadata
        )
    
    except Exception as e:
        import logging
        logging.getLogger("Pipeline").warning(f"Failed to parse LLM response: {e}")
        return None

