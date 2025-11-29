"""
Adda P-Bot API Server v5
Main entrypoint for the Flask API.
"""
import os
import sys
import logging
from flask import Flask, request, jsonify
from flask_cors import CORS

# Add parent directory to path to allow imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.engine import AddaSearchEngine

# Configure Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - SERVER - %(levelname)s - %(message)s')
logger = logging.getLogger("ADDA_SERVER")

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Initialize the Search Engine
try:
    engine = AddaSearchEngine()
    logger.info("AddaSearchEngine v5 initialized successfully")
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
        "session_state": dict (optional)
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
                "show_upload_button": True
            })

        # Run the engine with session state for persistence
        session_state = data.get('session_state')
        result = engine.run(user_message, history, session_state)
        
        # Extract data for UI directives
        current_state = result.get('current_state', {})
        thoughts = result.get('thoughts', {})
        
        # Build UI directives for frontend
        target_step = thoughts.get('target_step', 'step_1_intake')
        step_titles = {
            'step_1_intake': 'Steg 1: Beskriv Behov',
            'step_2_level': 'Steg 2: Kompetensnivå',
            'step_3_volume': 'Steg 3: Volym & Pris',
            'step_4_strategy': 'Steg 4: Avropsform',
            'general': 'Allmänt'
        }
        
        ui_directives = {
            "entity_summary": current_state.get('extracted_entities', {}),
            "update_sticky_header": step_titles.get(target_step, 'Resursupphandling'),
            "set_active_process_step": target_step,
            "missing_info": current_state.get('missing_info', []),
            "current_intent": current_state.get('current_intent', 'INSPIRATION')
        }
        
        response = {
            "message": result.get('response', "Ursäkta, jag kunde inte generera ett svar."),
            "thoughts": result.get('thoughts', {}),
            "sources": result.get('sources', []),
            "current_state": current_state,
            "ui_directives": ui_directives
        }
        
        return jsonify(response)

    except Exception as e:
        logger.error(f"Error in conversation endpoint: {e}")
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
    return jsonify({"status": "ok", "version": "5.0"})


def main():
    """Main entry point."""
    port = int(os.environ.get('PORT', 5000))
    logger.info(f"Starting Adda P-Bot API v5 on port {port}")
    app.run(host='0.0.0.0', port=port, debug=True)


if __name__ == '__main__':
    main()

