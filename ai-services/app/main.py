"""
Adda P-Bot API Server v5.24
Main entrypoint for the Flask API.

v5.24 Changes:
- All components now use pure dicts (no Pydantic models)
- AvropsContainerManager handles entity changes (deterministic)
- Planner extracts entities, Synthesizer only generates response
"""
import os
import sys
import logging
from flask import Flask, request, jsonify
from flask_cors import CORS

from .engine import AddaSearchEngine

# Configure Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - SERVER - %(levelname)s - %(message)s')
logger = logging.getLogger("ADDA_SERVER")

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Initialize the Search Engine
try:
    engine = AddaSearchEngine()
    logger.info("AddaSearchEngine v5.24 initialized successfully")
except Exception as e:
    logger.critical(f"Failed to initialize AddaSearchEngine: {e}")
    sys.exit(1)


@app.route('/api/conversation', methods=['POST'])
def conversation():
    """
    Handle chat conversation.
    Expected JSON body:
    {
        "user_message": str,
        "conversation_history": list,
        "session_state": dict (optional, legacy),
        "avrop_data": dict (optional, v5.4 - preferred)
    }
    
    Returns:
    {
        "message": str,
        "sources": list,
        "reasoning": dict,
        "avrop_data": dict (v5.4 - new AvropsData),
        "avrop_progress": dict (v5.4 - completion info),
        "current_state": dict (legacy, for backward compatibility),
        "ui_directives": dict
    }
    """
    try:
        data = request.json
        user_message = data.get('user_message')
        history = data.get('conversation_history', [])
        
        # Log the incoming request
        logger.info(f"Received message: {user_message}")
        
        # If no user message (initial load), provide a welcome message
        if not user_message:
            return jsonify({
                "message": "Hej! Jag är din AI-assistent för resursupphandling. Vad behöver du hjälp med idag?",
                "input_placeholder": "T.ex. 'Jag behöver en projektledare'",
                "show_upload_button": True,
                "avrop_data": {"resources": [], "avrop_typ": None},
                "avrop_progress": {"completion_percent": 0, "is_complete": False, "missing_fields": ["resources"]},
                "ui_directives": {
                    "entity_summary": {},
                    "update_sticky_header": "Steg 1: Beskriv Behov",
                    "set_active_process_step": "step_1_needs",
                    "missing_info": ["resources"],
                    "current_intent": "INSPIRATION",
                    "completion_percent": 0,
                    "avrop_typ": None
                }
            })

        # Get avrop_data from request (v5.24: pure dict)
        avrop_data = data.get('avrop_data')
        session_state = data.get('session_state')
        
        result = engine.run(user_message, history, session_state, avrop_data)
        
        # Extract data from v5.4 format
        current_state = result.get('current_state', {})
        reasoning = result.get('reasoning', {})
        engine_ui_directives = result.get('ui_directives', {})
        avrop_data_result = result.get('avrop_data', {})
        avrop_progress = result.get('avrop_progress', {})
        
        # Map target_step to human-readable header
        target_step = engine_ui_directives.get('target_step', 'step_1_intake')
        step_titles = {
            'step_1_intake': 'Steg 1: Beskriv Behov',
            'step_1_needs': 'Steg 1: Beskriv Behov',
            'step_2_level': 'Steg 2: Kompetensnivå',
            'step_3_volume': 'Steg 3: Volym & Pris',
            'step_4_strategy': 'Steg 4: Avropsform',
            'general': 'Allmänt'
        }
        
        # Build UI directives for frontend (matching expected format)
        ui_directives = {
            "entity_summary": engine_ui_directives.get('entity_summary', {}),
            "update_sticky_header": step_titles.get(target_step, 'Resursupphandling'),
            "set_active_process_step": target_step,
            "missing_info": engine_ui_directives.get('missing_info', []),
            "current_intent": engine_ui_directives.get('current_intent', 'INSPIRATION'),
            # v5.2 fields
            "detected_topics": engine_ui_directives.get('detected_topics', []),
            "taxonomy_branches": engine_ui_directives.get('taxonomy_branches', []),
            "ghost_mode": engine_ui_directives.get('ghost_mode', False),
            "tone": engine_ui_directives.get('tone', 'Informative'),
            "has_warning": engine_ui_directives.get('has_warning', False),
            # v5.4 fields
            "avrop_typ": engine_ui_directives.get('avrop_typ'),
            "resource_count": engine_ui_directives.get('resource_count', 0),
            "completion_percent": engine_ui_directives.get('completion_percent', 0),
            "is_complete": engine_ui_directives.get('is_complete', False),
            "constraint_violations": engine_ui_directives.get('constraint_violations', [])
        }
        
        response = {
            "message": result.get('response', "Ursäkta, jag kunde inte generera ett svar."),
            "sources": result.get('sources', []),
            "reasoning": reasoning,
            # v5.4: New avrop fields
            "avrop_data": avrop_data_result,
            "avrop_progress": avrop_progress,
            # Session state - frontend expects "session_state" key
            "session_state": current_state,
            "current_state": current_state,  # Keep for backward compatibility
            "ui_directives": ui_directives
        }
        
        return jsonify(response)

    except Exception as e:
        logger.error(f"Error in conversation endpoint: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e), "message": "Ett fel uppstod på servern."}), 500


@app.route('/api/analyze-document', methods=['POST'])
def analyze_document():
    """
    Stub for document analysis.
    """
    return jsonify({
        "message": "Filuppladdning är inte implementerad än i denna version.",
        "resources": [],
        "summary": "Funktionen är under utveckling."
    })


@app.route('/api/health', methods=['GET'])
def health():
    """Health check endpoint."""
    return jsonify({"status": "ok", "version": "5.24"})


def main():
    """Main entry point."""
    port = int(os.environ.get('PORT', 5000))
    logger.info(f"Starting Adda P-Bot API v5.24 on port {port}")
    # use_reloader=False prevents double initialization (which causes Kuzu lock)
    app.run(host='0.0.0.0', port=port, debug=True, use_reloader=False)


if __name__ == '__main__':
    main()
