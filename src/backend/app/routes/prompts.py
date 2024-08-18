from app.utils.schema_to_model_builder import SchemaToModelBuilder
import logging
import json
import traceback
from jsonschema import validate, ValidationError
from flask import Blueprint, jsonify, request
from app.models import Prompt
from app.extensions import db


schema_ref = SchemaToModelBuilder.load_swagger_definition()
schema_builder = SchemaToModelBuilder(schema_ref['components']['schemas']['StreamResponse']['properties'])

prompts_blueprint = Blueprint('prompts', __name__)
logger = logging.getLogger(__name__)



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
        prompt = data.get('prompt', None)
        prompt_id = data.get('prompt_id', None)
        # Validate request data against the schema
        try:
            validate(instance=data, schema=schema_ref)
            logger.info("Request data passed schema validation")
        except ValidationError as validation_error:
            error_message = validation_error.message
            logger.error(f"Validation error: {error_message}")
            return json.dumps(schema_builder.create_object(status="validation-error",prompt=prompt, prompt_id=prompt_id, message=error_message,)), 400

        # Check if the prompt already exists
        existing_prompt = Prompt.query.filter_by(prompt=prompt).first()
        if existing_prompt:
            logger.info(f"Prompt already exists with id: {existing_prompt.id}")
            json.dumps(schema_builder.create_object(status="prompt-not-changed",prompt= data.get('prompt', None), prompt_id=prompt_id,message="no action required")), 200

        # Save the new prompt if it does not already exist
        storedPrompt = Prompt(prompt=prompt)
        db.session.add(storedPrompt)
        db.session.commit()

        logger.info(f"Prompt saved successfully with id: {storedPrompt.id}")
        return  json.dumps(schema_builder.create_object(status="prompt-saved",prompt=storedPrompt.prompt, prompt_id=str(storedPrompt.id), message="promt was saved")), 200
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
