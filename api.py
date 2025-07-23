#!/usr/bin/env python3
"""
Flask API for AI Router

This API provides HTTP endpoints for the intelligent AI model router.
It supports routing requests to the best model, parallel model calls,
and response synthesis.
"""

import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
from typing import Dict, Any
import logging
from router import AIRouter

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize router with API keys from environment
config = {
    "openai": {"api_key": os.getenv("OPENAI_API_KEY")},
    "anthropic": {"api_key": os.getenv("ANTHROPIC_API_KEY")},
    "google": {"api_key": os.getenv("GOOGLE_API_KEY")},
    "xai": {"api_key": os.getenv("XAI_API_KEY")}
}

# Create global router instance
router = AIRouter(config)

def validate_request_data(data: Dict[str, Any]) -> tuple[bool, str]:
    """Validate incoming request data"""
    if not data:
        return False, "Request body is required"
    
    if 'messages' not in data:
        return False, "messages field is required"
    
    if not isinstance(data['messages'], list):
        return False, "messages must be a list"
    
    if len(data['messages']) == 0:
        return False, "messages list cannot be empty"
    
    # Validate message format
    for msg in data['messages']:
        if not isinstance(msg, dict):
            return False, "Each message must be a dictionary"
        if 'role' not in msg or 'content' not in msg:
            return False, "Each message must have 'role' and 'content' fields"
    
    return True, ""

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "service": "AI Router API",
        "version": "1.0.0"
    })

@app.route('/models', methods=['GET'])
def list_models():
    """List available models and their profiles"""
    models_info = {}
    for key, profile in router.models.items():
        models_info[key] = {
            "name": profile.name,
            "provider": profile.provider,
            "model_id": profile.model_id,
            "strengths": profile.strengths,
            "cost_per_1k_tokens": profile.cost_per_1k_tokens
        }
    
    return jsonify({
        "models": models_info,
        "router_model": router.router_model
    })

@app.route('/route', methods=['POST'])
def route_request():
    """
    Route a request to the appropriate AI model
    
    Request body:
    {
        "messages": [{"role": "user", "content": "Your prompt here"}],
        "temperature": 0.7,  # optional
        "max_tokens": 1000   # optional
    }
    """
    try:
        data = request.get_json()
        
        # Validate request
        is_valid, error_msg = validate_request_data(data)
        if not is_valid:
            return jsonify({"error": error_msg}), 400
        
        # Extract parameters
        messages = data['messages']
        kwargs = {k: v for k, v in data.items() if k != 'messages'}
        
        # Route the request
        response = router.route(messages, **kwargs)
        
        # Format response
        return jsonify({
            "response": response.choices[0].message.content
        })
        
    except Exception as e:
        logger.error(f"Error in route_request: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/route_with_metadata', methods=['POST'])
def route_with_metadata_request():
    """
    Route a request and return metadata about the routing decision
    
    Request body same as /route
    """
    try:
        data = request.get_json()
        
        # Validate request
        is_valid, error_msg = validate_request_data(data)
        if not is_valid:
            return jsonify({"error": error_msg}), 400
        
        # Extract parameters
        messages = data['messages']
        kwargs = {k: v for k, v in data.items() if k != 'messages'}
        
        # Route with metadata
        response, metadata = router.route_with_metadata(messages, **kwargs)
        
        # Format response
        return jsonify({
            "response": response.choices[0].message.content,
            "metadata": metadata
        })
        
    except Exception as e:
        logger.error(f"Error in route_with_metadata: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/parallelbest', methods=['POST'])
def parallel_best_route():
    """
    Call all models in parallel and return the best response
    
    Request body same as /route
    """
    try:
        data = request.get_json()
        
        # Validate request
        is_valid, error_msg = validate_request_data(data)
        if not is_valid:
            return jsonify({"error": error_msg}), 400
        
        # Extract parameters
        messages = data['messages']
        kwargs = {k: v for k, v in data.items() if k != 'messages'}
        
        # Parallel best route
        response, metadata = router.parallelbest_route(messages, **kwargs)
        
        # Format response - return only the best response
        return jsonify({
            "response": response.choices[0].message.content
        })
        
    except Exception as e:
        logger.error(f"Error in parallel_best_route: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/parallelsynthetize', methods=['POST'])
def parallel_synthetize_route():
    """
    Call models in parallel and synthesize their responses
    
    Request body same as /route
    """
    try:
        data = request.get_json()
        
        # Validate request
        is_valid, error_msg = validate_request_data(data)
        if not is_valid:
            return jsonify({"error": error_msg}), 400
        
        # Extract parameters
        messages = data['messages']
        kwargs = {k: v for k, v in data.items() if k != 'messages'}
        
        # Parallel synthetize route
        response, metadata = router.parallelsynthetize_route(messages, **kwargs)
        
        # Format response - return only the synthesized response
        return jsonify({
            "response": response.choices[0].message.content
        })
        
    except Exception as e:
        logger.error(f"Error in parallel_synthetize_route: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/analyze', methods=['POST'])
def analyze_prompt():
    """
    Analyze a prompt without sending it to any model
    
    Request body:
    {
        "prompt": "Your prompt text here"
    }
    """
    try:
        data = request.get_json()
        
        if not data or 'prompt' not in data:
            return jsonify({"error": "prompt field is required"}), 400
        
        # Analyze the prompt
        analysis = router.analyze_prompt(data['prompt'])
        
        return jsonify(analysis)
        
    except Exception as e:
        logger.error(f"Error in analyze_prompt: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({"error": "Endpoint not found"}), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    return jsonify({"error": "Internal server error"}), 500

if __name__ == '__main__':
    # Get port from environment or use default
    port = int(os.getenv('PORT', 5000))
    
    # Check if API keys are configured
    if not any([os.getenv("OPENAI_API_KEY"), os.getenv("ANTHROPIC_API_KEY"), 
                os.getenv("GOOGLE_API_KEY"), os.getenv("XAI_API_KEY")]):
        logger.warning("No API keys found in environment. Make sure to set them in .env file")
    
    # Run the Flask app
    app.run(host='0.0.0.0', port=port, debug=os.getenv('DEBUG', 'False').lower() == 'true')