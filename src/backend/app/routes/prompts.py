from flask import Blueprint, jsonify, request
from app.models import Prompt
from app.extensions import db
from jsonschema import validate, ValidationError
import logging
import traceback

prompts_blueprint = Blueprint('prompts', __name__)
logger = logging.getLogger(__name__)

# Define the JSON schema for the save_prompt request
save_prompt_schema = {
    "type": "object",
    "properties": {
        "prompt": {"type": "string"}
    },
    "required": ["prompt"],
    "additionalProperties": False  # Ensures no extra fields are allowed
}

@prompts_blueprint.route('/load_prompts', methods=['GET'])
def load_prompts_route():
    logger.info("Loading prompts for client")
    prompts = Prompt.query.order_by(Prompt.timestamp.desc()).all()
    return jsonify([prompt.to_dict() for prompt in prompts])

@prompts_blueprint.route('/save_prompt', methods=['POST'])
def save_prompt_route():
    try:
        data = request.json
        logger.info(f"Received save_prompt request with data: {data}")

        # Validate request data against the schema
        try:
            validate(instance=data, schema=save_prompt_schema)
            logger.info("Request data passed schema validation")
        except ValidationError as validation_error:
            error_message = validation_error.message
            logger.error(f"Validation error: {error_message}")
            return jsonify({"error": error_message}), 400

        new_prompt = data.get('prompt', None)
        if new_prompt is None:
            logger.warning("'prompt' is a required property")
            return jsonify({"error": "'prompt' is a required property"}), 400
        elif not new_prompt.strip():  # Check if the prompt is empty or just whitespace
            logger.warning("No prompt provided for saving")
            return jsonify({"error": "No prompt provided"}), 400

        prompt = Prompt(prompt=new_prompt)
        db.session.add(prompt)
        db.session.commit()

        logger.info(f"Prompt saved successfully with id: {prompt.id}")
        return jsonify({"status": "Prompt saved successfully", "id": str(prompt.id)}), 200
    except Exception as e:
        db.session.rollback()
        logger.error(f"Unexpected error in save_prompt: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({"error": "An unexpected error occurred"}), 500

@prompts_blueprint.route('/delete_prompt/<uuid:id>', methods=['DELETE'])
def delete_prompt_route(id):
    try:
        logger.info(f"Attempting to delete prompt with id: {id}")
        prompt = Prompt.query.get(id)
        if prompt:
            db.session.delete(prompt)
            db.session.commit()
            logger.info(f"Prompt with id {id} deleted successfully")
            return jsonify({"status": "Prompt deleted successfully"}), 200
        else:
            logger.warning(f"Prompt with id {id} not found")
            return jsonify({"error": "Prompt not found"}), 404
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error in delete_prompt: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({"error": str(e)}), 500
