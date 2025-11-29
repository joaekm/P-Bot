"""
Response Models for AI Services

Strict Pydantic models defining the contract between backend and frontend.
All AI responses MUST conform to these schemas.
"""

from typing import List, Optional, Dict, Any, Literal
from pydantic import BaseModel, Field


class ResourceItem(BaseModel):
    """A single resource/role in the manifest"""
    role: str = Field(..., description="Role name, e.g. 'Javautvecklare'")
    quantity: int = Field(default=1, description="Number of people needed")
    location: Optional[str] = Field(default=None, description="Location/region")
    level: Optional[int] = Field(default=None, ge=1, le=5, description="Competence level 1-5")
    hours: Optional[int] = Field(default=None, description="Estimated hours")
    estimated_cost: Optional[float] = Field(default=None, description="Estimated cost in SEK")
    source: Literal["user", "ai", "document"] = Field(default="user", description="How this resource was added")


class UIStreamWidget(BaseModel):
    """
    A widget that renders in the chat stream.
    
    The frontend will look up widget_type in a component registry
    and render it with the provided props.
    """
    widget_type: str = Field(
        ..., 
        description="Component type, e.g. 'ResourceSummaryCard', 'LevelSelector', 'CostEstimate'"
    )
    props: Dict[str, Any] = Field(
        default_factory=dict,
        description="Props to pass to the component"
    )


class UIActionPanel(BaseModel):
    """
    Controls the input zone at the bottom of the chat.
    
    The frontend renders this area based on the mode:
    - text_input: Show text field with placeholder
    - binary_choice: Show only buttons from actions array
    - file_upload: Show file upload button
    - locked: No input allowed (processing)
    """
    mode: Literal["text_input", "binary_choice", "file_upload", "locked"] = Field(
        default="text_input",
        description="Input mode for the action panel"
    )
    placeholder: Optional[str] = Field(
        default=None,
        description="Placeholder text for text_input mode"
    )
    actions: List[Dict[str, str]] = Field(
        default_factory=list,
        description="Button actions for binary_choice mode. Each dict has 'label' and 'value' keys."
    )


class SourceDocument(BaseModel):
    """
    An uploaded document stored in the session.
    
    This is PRIVATE session data - never stored in ChromaDB.
    The full_text is injected into the LLM prompt for context.
    """
    filename: str = Field(..., description="Original filename")
    full_text: str = Field(..., description="Full extracted text content")
    uploaded_at: str = Field(..., description="ISO timestamp of upload")


class SessionState(BaseModel):
    """
    The persistent memory across the conversation.
    
    This is the "suitcase" that travels between steps.
    Frontend sends this back with each request.
    
    Contains both:
    - resource_manifest: Extracted/confirmed resources
    - source_documents: Uploaded files (PRIVATE, session-only)
    """
    resource_manifest: List[ResourceItem] = Field(
        default_factory=list,
        description="The list of resources/roles being procured"
    )
    source_documents: List[SourceDocument] = Field(
        default_factory=list,
        description="Uploaded documents with full text (session-private, NOT in ChromaDB)"
    )
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional context: levels_set, volumes, procurement_method, etc."
    )
    current_step: str = Field(
        default="step_1_needs",
        description="Current step ID"
    )


class AIResponse(BaseModel):
    """
    The complete response from the backend.
    
    This is the contract between backend and frontend.
    Every /api/conversation response MUST conform to this schema.
    """
    text_content: str = Field(
        ...,
        description="The AI's text message to display"
    )
    stream_widget: Optional[UIStreamWidget] = Field(
        default=None,
        description="Optional widget to render in the chat stream"
    )
    action_panel: UIActionPanel = Field(
        default_factory=UIActionPanel,
        description="Configuration for the input zone"
    )
    session_state: SessionState = Field(
        default_factory=SessionState,
        description="Updated session state to persist"
    )
    is_step_complete: bool = Field(
        default=False,
        description="Whether the current step is complete and ready to advance"
    )
    next_step: Optional[str] = Field(
        default=None,
        description="The next step to advance to (if is_step_complete is True)"
    )
    error: Optional[str] = Field(
        default=None,
        description="Error message if something went wrong"
    )


# =============================================================================
# STEP CONFIGURATION
# =============================================================================

STEP_SEQUENCE = [
    "step_1_needs",
    "step_2_level", 
    "step_3_volume",
    "step_4_strategy"
]

STEP_METADATA = {
    "step_1_needs": {
        "title": "Beskriv Behov",
        "process_step": 1,
        "description": "Samla in information om roller, antal och plats"
    },
    "step_2_level": {
        "title": "Bedöm Kompetensnivå",
        "process_step": 2,
        "description": "Välj kompetensnivå (1-5) för varje roll"
    },
    "step_3_volume": {
        "title": "Volym & Pris",
        "process_step": 3,
        "description": "Ange timmar och få prisuppskattning"
    },
    "step_4_strategy": {
        "title": "Avropsform & Strategi",
        "process_step": 4,
        "description": "Bestäm avropsform (DR/FKU) och slutför"
    }
}


def get_next_step(current_step: str) -> Optional[str]:
    """Get the next step in the sequence, or None if at the end."""
    try:
        current_index = STEP_SEQUENCE.index(current_step)
        if current_index < len(STEP_SEQUENCE) - 1:
            return STEP_SEQUENCE[current_index + 1]
    except ValueError:
        pass
    return None


def get_step_metadata(step_id: str) -> Dict[str, Any]:
    """Get metadata for a step."""
    return STEP_METADATA.get(step_id, {
        "title": "Okänt steg",
        "process_step": 0,
        "description": ""
    })

