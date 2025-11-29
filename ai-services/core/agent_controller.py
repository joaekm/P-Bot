"""
Agent Controller - The Relay Pattern

This module implements the core logic for loading and executing
step-specific agents with isolated knowledge scopes.
"""

import os
import json
import logging
from typing import Optional, Dict, Any, List
from pathlib import Path

from .response_models import (
    SessionState,
    SourceDocument,
    AIResponse,
    UIActionPanel,
    UIStreamWidget,
    ResourceItem,
    get_next_step,
    get_step_metadata,
    STEP_SEQUENCE
)

logger = logging.getLogger(__name__)

# Base path for agents directory
AGENTS_DIR = Path(__file__).parent.parent / "agents"


class AgentController:
    """
    The Relay - loads and executes step-specific agents.
    
    Each step has:
    - system_prompt.md: The AI's instructions
    - context_manifest.json: RAG filter configuration
    
    The controller:
    1. Loads the appropriate prompt and manifest
    2. Configures RAG to only search allowed categories
    3. Executes the LLM call
    4. Validates and returns the response
    """
    
    def __init__(self, step_id: str, session_state: Optional[SessionState] = None):
        """
        Initialize the controller for a specific step.
        
        Args:
            step_id: The step identifier (e.g., "step_1_needs")
            session_state: The current session state (optional)
        """
        self.step_id = step_id
        self.session_state = session_state or SessionState()
        
        # Validate step exists
        if step_id not in STEP_SEQUENCE:
            logger.warning(f"Unknown step_id: {step_id}, defaulting to step_1_needs")
            self.step_id = "step_1_needs"
        
        # Load configuration
        self.prompt = self._load_prompt()
        self.manifest = self._load_manifest()
        self.metadata = get_step_metadata(self.step_id)
        
        logger.info(f"AgentController initialized for {self.step_id}")
    
    def _load_prompt(self) -> str:
        """Load the system prompt from the agent's directory."""
        prompt_path = AGENTS_DIR / self.step_id / "system_prompt.md"
        
        try:
            with open(prompt_path, 'r', encoding='utf-8') as f:
                prompt = f.read()
                logger.debug(f"Loaded prompt from {prompt_path} ({len(prompt)} chars)")
                return prompt
        except FileNotFoundError:
            logger.error(f"Prompt file not found: {prompt_path}")
            return self._get_fallback_prompt()
        except Exception as e:
            logger.error(f"Error loading prompt: {e}")
            return self._get_fallback_prompt()
    
    def _load_manifest(self) -> Dict[str, Any]:
        """Load the context manifest from the agent's directory."""
        manifest_path = AGENTS_DIR / self.step_id / "context_manifest.json"
        
        try:
            with open(manifest_path, 'r', encoding='utf-8') as f:
                manifest = json.load(f)
                logger.debug(f"Loaded manifest from {manifest_path}: {manifest}")
                return manifest
        except FileNotFoundError:
            logger.warning(f"Manifest file not found: {manifest_path}")
            return {"allowed_categories": [], "specific_files": []}
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in manifest: {e}")
            return {"allowed_categories": [], "specific_files": []}
        except Exception as e:
            logger.error(f"Error loading manifest: {e}")
            return {"allowed_categories": [], "specific_files": []}
    
    def _get_fallback_prompt(self) -> str:
        """Return a basic fallback prompt if the main one fails to load."""
        return """
Du är en hjälpsam assistent för IT-konsultupphandling.
Svara alltid på svenska och i JSON-format.

{
  "text_content": "Ditt meddelande",
  "stream_widget": null,
  "action_panel": {
    "mode": "text_input",
    "placeholder": "Skriv här...",
    "actions": []
  },
  "session_state": {
    "resource_manifest": [],
    "metadata": {}
  },
  "is_step_complete": false
}
"""
    
    def get_rag_filter(self) -> Dict[str, Any]:
        """
        Get the RAG filter configuration for this step.
        
        Returns:
            Dict with 'allowed_categories' and 'specific_files'
        """
        return {
            "allowed_categories": self.manifest.get("allowed_categories", []),
            "specific_files": self.manifest.get("specific_files", [])
        }
    
    def get_allowed_categories(self) -> List[str]:
        """Get the list of allowed RAG categories for this step."""
        return self.manifest.get("allowed_categories", [])
    
    def build_system_prompt(self) -> str:
        """
        Build the complete system prompt with session state context.
        
        Includes:
        - Base system prompt from file
        - Injected source_documents (full text from uploaded files)
        - Current session state (resource_manifest, metadata)
        - Step information
        
        Returns:
            The full prompt string to send to the LLM
        """
        prompt_parts = [self.prompt]
        
        # Inject source documents if present (Session-Based Data)
        # This is PRIVATE session data - NOT from ChromaDB
        if self.session_state.source_documents:
            doc_context = "\n\n## Uploaded Documents (Session Context)\n\n"
            doc_context += "The user has uploaded the following documents. Use this information to answer questions and extract data.\n\n"
            for doc in self.session_state.source_documents:
                doc_context += f"--- START: {doc.filename} (uploaded: {doc.uploaded_at}) ---\n"
                doc_context += doc.full_text
                doc_context += f"\n--- END: {doc.filename} ---\n\n"
            prompt_parts.append(doc_context)
        
        # Add current session state (without source_documents to avoid duplication)
        # Create a copy of session state without full document text for JSON
        state_for_json = {
            "resource_manifest": [r.model_dump() for r in self.session_state.resource_manifest],
            "source_documents": [{"filename": d.filename, "uploaded_at": d.uploaded_at} for d in self.session_state.source_documents],
            "metadata": self.session_state.metadata,
            "current_step": self.session_state.current_step
        }
        
        state_context = f"""
## Current Session State

```json
{json.dumps(state_for_json, indent=2, ensure_ascii=False)}
```

## Step Information
- Current Step: {self.step_id}
- Step Title: {self.metadata.get('title', 'Unknown')}
- Process Step: {self.metadata.get('process_step', 0)} of 4
"""
        prompt_parts.append(state_context)
        
        return "\n\n".join(prompt_parts)
    
    def validate_response(self, response_data: Dict[str, Any]) -> AIResponse:
        """
        Validate and parse the LLM response into an AIResponse.
        
        Preserves source_documents from the current session state
        (LLM should not modify these, only add new resources).
        
        Args:
            response_data: The parsed JSON from the LLM
            
        Returns:
            A validated AIResponse object
        """
        try:
            # Ensure session_state has current_step
            if "session_state" in response_data:
                response_data["session_state"]["current_step"] = self.step_id
                # IMPORTANT: Preserve source_documents from current session
                # LLM should not be able to modify or delete uploaded documents
                response_data["session_state"]["source_documents"] = [
                    doc.model_dump() for doc in self.session_state.source_documents
                ]
            else:
                response_data["session_state"] = {
                    "resource_manifest": [],
                    "source_documents": [doc.model_dump() for doc in self.session_state.source_documents],
                    "metadata": {},
                    "current_step": self.step_id
                }
            
            # Handle step completion
            if response_data.get("is_step_complete", False):
                next_step = get_next_step(self.step_id)
                response_data["next_step"] = next_step
                if next_step:
                    response_data["session_state"]["current_step"] = next_step
            
            # Validate with Pydantic
            return AIResponse(**response_data)
            
        except Exception as e:
            logger.error(f"Response validation failed: {e}")
            # Return error response
            return AIResponse(
                text_content="Ett fel uppstod vid bearbetning av svaret. Försök igen.",
                action_panel=UIActionPanel(
                    mode="text_input",
                    placeholder="Försök igen...",
                    actions=[]
                ),
                session_state=self.session_state,
                is_step_complete=False,
                error=str(e)
            )
    
    def get_initial_action_panel(self) -> UIActionPanel:
        """Get the default action panel for this step."""
        if self.step_id == "step_1_needs":
            return UIActionPanel(
                mode="text_input",
                placeholder="Beskriv ditt behov eller ladda upp ett underlag...",
                actions=[]
            )
        elif self.step_id == "step_2_level":
            return UIActionPanel(
                mode="binary_choice",
                placeholder=None,
                actions=[
                    {"label": "Nivå 1 (Junior)", "value": "1"},
                    {"label": "Nivå 2 (Medior)", "value": "2"},
                    {"label": "Nivå 3 (Senior)", "value": "3"},
                    {"label": "Nivå 4 (Expert)", "value": "4"},
                    {"label": "Nivå 5 (Nyckelexpert)", "value": "5"}
                ]
            )
        elif self.step_id == "step_3_volume":
            return UIActionPanel(
                mode="text_input",
                placeholder="Antal timmar...",
                actions=[]
            )
        elif self.step_id == "step_4_strategy":
            return UIActionPanel(
                mode="binary_choice",
                placeholder=None,
                actions=[
                    {"label": "Slutför avrop", "value": "COMPLETE"},
                    {"label": "Ändra något", "value": "EDIT"}
                ]
            )
        else:
            return UIActionPanel(
                mode="text_input",
                placeholder="Skriv här...",
                actions=[]
            )


def reload_agent(step_id: str) -> AgentController:
    """
    Create a fresh AgentController, reloading prompt from disk.
    
    This enables hot-reloading of prompts during development.
    """
    return AgentController(step_id)


def list_available_steps() -> List[Dict[str, Any]]:
    """
    List all available steps with their metadata.
    
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

