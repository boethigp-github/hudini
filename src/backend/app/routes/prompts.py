from flask import Blueprint, jsonify, request
from app.utils.helpers import load_prompts, save_prompts
import uuid
from datetime import datetime
from jsonschema import validate, ValidationError
import logging
import traceback

prompts_blueprint = Blueprint('prompts', __name__)
logger = logging.getLogger(__name__)

# Global variable for prompts
prompts = load_prompts()

@prompts_blueprint.route('/load_prompts', methods=['GET'])
def load_prompts_route():
    logger.info("Loading prompts for client")
    return jsonify(prompts)

@prompts_blueprint.route('/save_prompt', methods=['POST'])
def save_prompt_route():
    global prompts
    try:
        data = request.json
        logger.info(f"Received save_prompt request with data: {data}")

        # Validate request data against the schema
        save_prompt_schema = {}  # Define or load this schema as needed
        try:
            validate(instance=data, schema=save_prompt_schema)
            logger.info("Request data passed schema validation")
        except ValidationError as validation_error:
            error_message = f"Invalid request: {validation_error.message}"
            logger.error(f"Validation error: {error_message}")
            return jsonify({"error": error_message}), 400

        new_prompt = data.get('prompt', '')
        if not new_prompt:
            logger.warning("No prompt provided for saving")
            return jsonify({"error": "No prompt provided"}), 400

        prompt_id = str(uuid.uuid4())
        prompts.append({
            "id": prompt_id,
            "prompt": new_prompt,
            "timestamp": datetime.now().isoformat()
        })
        prompts.sort(key=lambda x: x['timestamp'], reverse=True)
        save_prompts(prompts)

        logger.info(f"Prompt saved successfully with id: {prompt_id}")
        return jsonify({"status": "Prompt saved successfully", "id": prompt_id}), 200
    except Exception as e:
        logger.error(f"Unexpected error in save_prompt: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({"error": "An unexpected error occurred"}), 500

@prompts_blueprint.route('/delete_prompt/<string:id>', methods=['DELETE'])
def delete_prompt_route(id):
    global prompts
    try:
        logger.info(f"Attempting to delete prompt with id: {id}")
        original_length = len(prompts)
        prompts = [p for p in prompts if p['id'] != id]
        if len(prompts) < original_length:
            save_prompts(prompts)
            logger.info(f"Prompt with id {id} deleted successfully")
            return jsonify({"status": "Prompt deleted successfully"}), 200
        else:
            logger.warning(f"Prompt with id {id} not found")
            return jsonify({"error": "Prompt not found"}), 404
    except Exception as e:
        logger.error(f"Error in delete_prompt: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({"error": str(e)}), 500
