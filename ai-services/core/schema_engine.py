"""
Schema Engine - JSON Validation and Parsing

Utilities for parsing and validating LLM responses against our schemas.
"""

import json
import logging
import re
from typing import Dict, Any, Optional

from .response_models import AIResponse, SessionState, UIActionPanel

logger = logging.getLogger(__name__)


def extract_json_from_response(response_text: str) -> Optional[Dict[str, Any]]:
    """
    Extract JSON from an LLM response that may contain markdown or other text.
    
    Handles:
    - Pure JSON responses
    - JSON in ```json code blocks
    - JSON in ``` code blocks
    - JSON embedded in text
    
    Args:
        response_text: The raw response from the LLM
        
    Returns:
        Parsed JSON dict, or None if parsing fails
    """
    if not response_text:
        return None
    
    response_text = response_text.strip()
    
    # Try 1: Direct JSON parse
    try:
        return json.loads(response_text)
    except json.JSONDecodeError:
        pass
    
    # Try 2: Extract from ```json code block
    json_block_match = re.search(r'```json\s*([\s\S]*?)\s*```', response_text)
    if json_block_match:
        try:
            return json.loads(json_block_match.group(1).strip())
        except json.JSONDecodeError:
            pass
    
    # Try 3: Extract from ``` code block (no language specified)
    code_block_match = re.search(r'```\s*([\s\S]*?)\s*```', response_text)
    if code_block_match:
        try:
            return json.loads(code_block_match.group(1).strip())
        except json.JSONDecodeError:
            pass
    
    # Try 4: Find JSON object in text
    brace_start = response_text.find('{')
    brace_end = response_text.rfind('}')
    
    if brace_start != -1 and brace_end != -1 and brace_end > brace_start:
        try:
            return json.loads(response_text[brace_start:brace_end + 1])
        except json.JSONDecodeError:
            pass
    
    logger.warning(f"Could not extract JSON from response: {response_text[:200]}...")
    return None


def validate_ai_response(data: Dict[str, Any]) -> AIResponse:
    """
    Validate a dict against the AIResponse schema.
    
    Args:
        data: The parsed JSON dict
        
    Returns:
        Validated AIResponse object
        
    Raises:
        ValueError: If validation fails
    """
    try:
        return AIResponse(**data)
    except Exception as e:
        raise ValueError(f"Invalid AIResponse: {e}")


def create_error_response(
    message: str,
    session_state: Optional[SessionState] = None,
    error_details: Optional[str] = None
) -> AIResponse:
    """
    Create a standardized error response.
    
    Args:
        message: User-facing error message
        session_state: Current session state to preserve
        error_details: Technical error details for logging
        
    Returns:
        AIResponse with error information
    """
    return AIResponse(
        text_content=message,
        stream_widget=None,
        action_panel=UIActionPanel(
            mode="text_input",
            placeholder="Försök igen...",
            actions=[]
        ),
        session_state=session_state or SessionState(),
        is_step_complete=False,
        error=error_details
    )


def create_fallback_response(
    raw_text: str,
    session_state: Optional[SessionState] = None
) -> AIResponse:
    """
    Create a response when JSON parsing fails but we have text.
    
    The raw text is used as the message content.
    
    Args:
        raw_text: The raw LLM response text
        session_state: Current session state to preserve
        
    Returns:
        AIResponse with the raw text as message
    """
    return AIResponse(
        text_content=raw_text,
        stream_widget=None,
        action_panel=UIActionPanel(
            mode="text_input",
            placeholder="Skriv här...",
            actions=[]
        ),
        session_state=session_state or SessionState(),
        is_step_complete=False
    )


def merge_session_states(
    current: SessionState,
    update: Dict[str, Any]
) -> SessionState:
    """
    Merge an update dict into the current session state.
    
    Handles:
    - Updating resource_manifest (replaces if provided)
    - Merging metadata (shallow merge)
    - Preserving current_step unless explicitly changed
    
    Args:
        current: The current session state
        update: Dict with updates to apply
        
    Returns:
        New SessionState with merged values
    """
    # Start with current values
    new_manifest = current.resource_manifest.copy()
    new_metadata = current.metadata.copy()
    new_step = current.current_step
    
    # Apply updates
    if "resource_manifest" in update and update["resource_manifest"]:
        # Replace manifest if provided
        new_manifest = update["resource_manifest"]
    
    if "metadata" in update and update["metadata"]:
        # Merge metadata
        new_metadata.update(update["metadata"])
    
    if "current_step" in update and update["current_step"]:
        new_step = update["current_step"]
    
    return SessionState(
        resource_manifest=new_manifest,
        metadata=new_metadata,
        current_step=new_step
    )



