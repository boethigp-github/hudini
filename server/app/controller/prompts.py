from server.app import SchemaToModelBuilder
import logging
import uuid
import traceback
from jsonschema import validate, ValidationError
from flask import Blueprint, jsonify, request
from server.app import Prompt
from server.app.extensions import db

# Load the Swagger definition and schema builder
schema_ref = SchemaToModelBuilder.load_swagger_definition()
schema_builder = SchemaToModelBuilder(schema_ref['components']['schemas']['StreamResponse']['properties'])

# Load the prompt schemas from the Swagger definition
prompt_schema = schema_ref['components']['schemas']['Prompt']

# Define the Flask blueprint
prompts_blueprint = Blueprint('prompts', __name__)
logger = logging.getLogger(__name__)

# Load saved prompts
@prompts_blueprint.route('/load_prompts', methods=['GET'])
def load_prompts_route():
    logger.info("Loading prompts for client")
    prompts = Prompt.query.order_by(Prompt.timestamp.desc()).all()
    return jsonify([prompt.to_dict() for prompt in prompts])

# Create a new prompt
@prompts_blueprint.route('/create_prompt', methods=['POST'])
def create_prompt_route():
    try:
        data = request.json
        logger.info(f"Received create_prompt request with data: {data}")

        # Validate request data against the create prompt schema
        try:
            validate(instance=data, schema=prompt_schema)
            logger.info("Request data passed schema validation")
        except ValidationError as validation_error:
            error_message = validation_error.message
            logger.error(f"Validation error: {error_message}")
            return jsonify({
                "status": "validation-error",
                "message": error_message,
            }), 400  # Return 400 Bad Request for validation errors

        # Save the new prompt
        new_prompt = Prompt(
            id=data.get('id', uuid.uuid4()),  # Ensure id is handled correctly
            prompt=data['prompt'],
            user=data['user'],
            status=data['status']  # Handle the status field
        )
        db.session.add(new_prompt)
        db.session.commit()

        logger.info(f"Prompt saved successfully with id: {new_prompt.id}")
        return jsonify({
            "status": "prompt-saved",
            "id": str(new_prompt.id),
            "prompt": new_prompt.prompt,
            "user": new_prompt.user,
            "status": new_prompt.status,  # Include status in response
            "timestamp": new_prompt.timestamp.isoformat()
        }), 200
    except Exception as e:
        db.session.rollback()
        logger.error(f"Unexpected error in create_prompt: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({
            "error": "333 An unexpected error occurred",
            "details": str(e)
        }), 500

# Update an existing prompt
@prompts_blueprint.route('/update_prompt/<uuid:id>', methods=['PATCH'])
def update_prompt_route(id):
    try:
        data = request.json
        logger.info(f"Received update_prompt request with data: {data}")

        # Validate request data against the update prompt schema
        try:
            validate(instance=data, schema=prompt_schema)
            logger.info("Request data passed schema validation")
        except ValidationError as validation_error:
            error_message = validation_error.message
            logger.error(f"Validation error: {error_message}")
            return jsonify({
                "status": "validation-error",
                "message": error_message,
            }), 400

        # Find the prompt by id
        prompt = Prompt.query.get(id)
        if not prompt:
            logger.warning(f"Prompt with id {id} not found")
            return jsonify({"error": "Prompt not found"}), 404

        # Update the prompt
        prompt.prompt = data['prompt']
        prompt.user = data['user']
        prompt.status = data['status']  # Handle the status field
        db.session.commit()

        logger.info(f"Prompt updated successfully with id: {id}")
        return jsonify({
            "id": str(id),
            "prompt": prompt.prompt,
            "user": prompt.user,
            "status": prompt.status,  # Include status in response
            "timestamp": prompt.timestamp.isoformat()
        }), 200
    except Exception as e:
        db.session.rollback()
        logger.error(f"Unexpected error in update_prompt: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({
            "error": "111An unexpected error occurred",
            "details": str(e)
        }), 500

# Delete a prompt by ID
@prompts_blueprint.route('/delete_prompt/<uuid:id>', methods=['DELETE'])
def delete_prompt_route(prompt_id):
    try:
        logger.info(f"Attempting to delete prompt with id: {prompt_id}")
        prompt = Prompt.query.get(prompt_id)
        if prompt:
            db.session.delete(prompt)
            db.session.commit()
            logger.info(f"Prompt with id {prompt_id} deleted successfully")
            return jsonify({"status": "Prompt deleted successfully"}), 200
        else:
            logger.warning(f"Prompt with id {prompt_id} not found")
            return jsonify({"error": "Prompt not found"}), 404
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error in delete_prompt: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({"error": str(e)}), 500
