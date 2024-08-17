# app/routes/models.py
import logging
from flask import Blueprint, jsonify
from app.services.model_service import get_local_models, get_openai_models

# Set up logger for this module
logger = logging.getLogger(__name__)

models_blueprint = Blueprint('models', __name__)

@models_blueprint.route('/get_models', methods=['GET'])
def get_models():
    try:
        local_models = get_local_models()
        openai_models = get_openai_models()  # Fetch models from OpenAI
        return jsonify({
            'local_models': local_models,
            'openai_models': openai_models
        })
    except Exception as e:
        logger.exception("An error occurred while fetching models.")
        return jsonify({"error": str(e)}), 500
