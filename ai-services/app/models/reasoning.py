"""
Reasoning Models for Adda Search Engine v5.2
Output models from the Planner (Logic Layer).
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Literal


class ReasoningPlan(BaseModel):
    """
    Output from PlannerComponent - the logical analysis for Synthesizer.
    
    This represents the "thinking" that happens between context retrieval
    and response generation. The Planner analyzes the context and creates
    a strategy for how the Synthesizer should respond.
    
    v5.3: Added validation_warnings and forced_strategy (absorbed from normalizer.py)
    """
    
    # Core reasoning
    primary_conclusion: str = Field(
        ..., 
        description="Kärnsvaret/logiken baserat på fakta från kontexten"
    )
    
    policy_check: str = Field(
        ..., 
        description="Vilken regel/policy styrde beslutet? (t.ex. '320-timmarsregeln från Prisbilaga 1')"
    )
    
    # Tone and style
    tone_instruction: Literal["Strict/Warning", "Helpful/Guiding", "Informative"] = Field(
        default="Informative",
        description="Hur ska Synthesizer formulera svaret?"
    )
    
    # Completeness
    missing_info: List[str] = Field(
        default_factory=list, 
        description="Saknad information för att ge ett 100% svar"
    )
    
    # Conflict handling
    conflict_resolution: Optional[str] = Field(
        default=None, 
        description="Om källor motsäger varandra - hur löstes konflikten?"
    )
    
    # Validation (legacy field, kept for backward compatibility)
    data_validation: Optional[str] = Field(
        default=None, 
        description="Om begäran var orimlig - varför? (t.ex. 'Volymen överstiger 320h-gränsen')"
    )
    
    # NEW: Validation warnings (absorbed from normalizer.py)
    validation_warnings: List[str] = Field(
        default_factory=list,
        description="Valideringsvarningar från regelkontroll (t.ex. '320h-regel triggad')"
    )
    
    # NEW: Forced strategy (absorbed from normalizer.py)
    forced_strategy: Optional[str] = Field(
        default=None,
        description="Strategi som tvingats av regelvalidering (t.ex. 'FKU' vid >320h)"
    )
    
    # Derived step for persona selection
    target_step: str = Field(
        default="general",
        description="Process-steg för persona-val (step_1_intake, step_3_volume, etc.)"
    )
    
    # Source tracking
    primary_sources: List[str] = Field(
        default_factory=list,
        description="Filnamn på PRIMARY-källor som användes"
    )
    
    secondary_sources: List[str] = Field(
        default_factory=list,
        description="Filnamn på SECONDARY-källor som användes (om tillåtet)"
    )
    
    def get_all_sources(self) -> List[str]:
        """Get all sources used in reasoning."""
        return self.primary_sources + self.secondary_sources
    
    def has_conflicts(self) -> bool:
        """Check if there were source conflicts."""
        return self.conflict_resolution is not None
    
    def requires_warning(self) -> bool:
        """Check if response should include a warning."""
        return (
            self.tone_instruction == "Strict/Warning" 
            or self.data_validation is not None
            or len(self.validation_warnings) > 0
        )
    
    def has_forced_strategy(self) -> bool:
        """Check if a strategy was forced by validation."""
        return self.forced_strategy is not None


class ReasoningContext(BaseModel):
    """
    Structured context summary for the Planner.
    Prepared from raw context documents.
    """
    
    primary_docs: List[dict] = Field(
        default_factory=list,
        description="Documents from PRIMARY authority"
    )
    
    secondary_docs: List[dict] = Field(
        default_factory=list,
        description="Documents from SECONDARY authority"
    )
    
    framework_specific_count: int = Field(
        default=0,
        description="Number of FRAMEWORK_SPECIFIC scope documents"
    )
    
    general_legal_count: int = Field(
        default=0,
        description="Number of GENERAL_LEGAL scope documents"
    )
    
    rule_count: int = Field(
        default=0,
        description="Number of RULE type documents"
    )
    
    has_conflicting_scopes: bool = Field(
        default=False,
        description="True if both FRAMEWORK_SPECIFIC and GENERAL_LEGAL are present"
    )

