"""
LLM Service - Gemini Integration with Agent Controller

This module handles communication with Google Gemini API,
using the new agent-scoped architecture.
"""

import os
import json
import logging
from typing import Optional, Dict, Any, List

import google.generativeai as genai
from dotenv import load_dotenv

from core.agent_controller import AgentController
from core.response_models import (
    AIResponse,
    SessionState,
    UIActionPanel,
    UIStreamWidget,
    ResourceItem,
    get_next_step,
    get_step_metadata,
    STEP_SEQUENCE,
    STEP_METADATA
)
from core.schema_engine import (
    extract_json_from_response,
    create_error_response,
    create_fallback_response
)

# Load environment variables
env_path = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(env_path)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configure Gemini
api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    logger.warning(f"GOOGLE_API_KEY not found. Checked .env at: {env_path}")
else:
    logger.info("GOOGLE_API_KEY loaded successfully")
    genai.configure(api_key=api_key)

# Initialize the model
model = genai.GenerativeModel('gemini-2.0-flash')


def generate_response(
    user_message: Optional[str],
    session_state: SessionState,
    conversation_history: Optional[List[Dict[str, str]]] = None,
    context_chunks: Optional[List[str]] = None
) -> AIResponse:
    """
    Generate an AI response using the agent controller.
    
    This is the main entry point for AI generation.
    It uses the AgentController to load the appropriate prompt
    and RAG context for the current step.
    
    Args:
        user_message: The user's message (None for initial message)
        session_state: The current session state
        conversation_history: List of previous messages
        context_chunks: RAG context chunks (already filtered by manifest)
    
    Returns:
        AIResponse object with the AI's response
    """
    if not api_key:
        return create_error_response(
            "Systemfel: API-nyckel saknas. Kontakta administratör.",
            session_state,
            "GOOGLE_API_KEY not configured"
        )
    
    current_step = session_state.current_step
    logger.info(f"Generating response for step: {current_step}")
    
    # Initialize agent controller
    controller = AgentController(current_step, session_state)
    
    # Build the full prompt
    system_prompt = controller.build_system_prompt()
    
    # Build conversation context
    history_text = ""
    if conversation_history:
        for msg in conversation_history[-10:]:  # Last 10 messages
            role = "Användare" if msg.get('role') == 'user' else "Assistent"
            history_text += f"{role}: {msg.get('content', '')}\n"
    
    # Build RAG context
    context_text = ""
    if context_chunks:
        context_text = "\n\n---\n\n".join(context_chunks)
    
    # Construct the full prompt
    full_prompt = f"""{system_prompt}

## RAG Context (Knowledge Base)
{context_text if context_text else "(Ingen kontext tillgänglig)"}

## Conversation History
{history_text if history_text else "(Ny konversation)"}

## User Message
{f"Användare: {user_message}" if user_message else "(Första meddelandet - välkomna användaren)"}

---
IMPORTANT: Respond ONLY with valid JSON matching the schema above. No other text.
"""

    try:
        response = model.generate_content(full_prompt)
        response_text = response.text.strip()
        
        logger.info(f"Raw AI response ({len(response_text)} chars): {response_text[:200]}...")
        
        # Parse JSON from response
        parsed = extract_json_from_response(response_text)
        
        if parsed is None:
            logger.warning("Could not parse JSON, using fallback response")
            return create_fallback_response(response_text, session_state)
        
        # Validate and return
        return controller.validate_response(parsed)
        
    except Exception as e:
        logger.error(f"Error generating response: {e}")
        return create_error_response(
            "Något gick fel. Försök igen.",
            session_state,
            str(e)
        )


def analyze_document(
    document_text: str,
    context_chunks: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Analyze an uploaded document to extract structured data.
    
    Args:
        document_text: Full text from uploaded document
        context_chunks: RAG context about roles/competence areas
    
    Returns:
        Dict with extracted resources
    """
    if not api_key:
        return {"error": "API-nyckel saknas", "resources": []}
    
    extraction_prompt = """
Du är en expert på att analysera behovsbeskrivningar och extrahera IT-konsultroller.

Analysera dokumentet och extrahera ALLA roller som efterfrågas.
För varje roll, identifiera:
- role: Rollnamn (t.ex. "Javautvecklare", "Projektledare")
- quantity: Antal personer (default 1)
- location: Plats om nämnd (t.ex. "Stockholm")

Svara ENDAST med JSON i detta format:
{
    "resources": [
        {"role": "...", "quantity": 1, "location": "..."}
    ],
    "summary": "Kort sammanfattning av behovet",
    "confidence": "high/medium/low"
}

DOKUMENT ATT ANALYSERA:
"""
    
    context_text = "\n\n".join(context_chunks) if context_chunks else ""
    
    full_prompt = f"""{extraction_prompt}

{document_text}

KONTEXT (Addas kompetensområden):
{context_text}
"""

    try:
        response = model.generate_content(full_prompt)
        response_text = response.text.strip()
        
        result = extract_json_from_response(response_text)
        
        if result is None:
            return {
                "resources": [],
                "summary": "Kunde inte analysera dokumentet",
                "error": "JSON parsing failed"
            }
        
        logger.info(f"Document analysis result: {result}")
        return result
        
    except Exception as e:
        logger.error(f"Error in document analysis: {e}")
        return {
            "resources": [],
            "summary": "Kunde inte analysera dokumentet",
            "error": str(e)
        }


def get_steps() -> List[Dict[str, Any]]:
    """
    Get the list of process steps with metadata.
    
    Returns:
        List of step info dicts
    """
    steps = []
    for step_id in STEP_SEQUENCE:
        metadata = get_step_metadata(step_id)
        steps.append({
            "id": step_id,
            "title": metadata.get("title", "Unknown"),
            "process_step": metadata.get("process_step", 0),
            "description": metadata.get("description", "")
        })
    return steps


def get_initial_message(step_id: str = "step_1_needs") -> AIResponse:
    """
    Get the initial message for a step.
    
    Args:
        step_id: The step to get initial message for
        
    Returns:
        AIResponse with initial message
    """
    session_state = SessionState(current_step=step_id)
    return generate_response(
        user_message=None,
        session_state=session_state,
        conversation_history=[],
        context_chunks=[]
    )
