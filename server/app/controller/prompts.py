
import logging
import uuid
import traceback
import logging
from flask import Blueprint, jsonify, Response
from jsonschema import validate, ValidationError
from flask import Blueprint, jsonify, request
from server.app.models.prompts import Prompt
from server.app.extensions import db

logger = logging.getLogger(__name__)

class PromptsController:
    def __init__(self):
        """
        Initializes the ModelsController instance.

        This method creates a Flask Blueprint for the models routes and registers the necessary routes.
        """
        # Create the blueprint for this controller
        self.blueprint = Blueprint('prompts', __name__)
        # Register the routes
        self.register_routes()

    def register_routes(self):
        """
        Registers routes to the Flask blueprint.

        This method maps the /models and /favicon.ico routes to their respective handler methods.
        """
        self.blueprint.add_url_rule('/prompt', 'prompts_route', self.prompts_route, methods=['GET'])
        self.blueprint.add_url_rule('/prompt', 'post_prompt_route', self.post_prompt_route, methods=['POST'])
        self.blueprint.add_url_rule('/prompt/<uuid:prompt_id>', 'delete_prompt_route', self.delete_prompt_route, methods=['DELETE'])
        self.blueprint.add_url_rule('/prompt/<uuid:prompt_id>', 'patch_prompt_route', self.patch_prompt_route, methods=['PATCH'])

    def prompts_route(self):
        logger.info("Loading prompts for client")
        prompts = Prompt.query.order_by(Prompt.timestamp.desc()).all()
        return jsonify([prompt.to_dict() for prompt in prompts])

    def post_prompt_route(self):
        try:
            data = request.json
            logger.info(f"Received prompt request with data: {data}")

            # Validate request data against the create prompt schema
            try:
                self.validateSchema(data)
                logger.info("Request data passed schema validation")
            except ValidationError as validation_error:
                error_message = validation_error.message
                logger.error(f"Validation error: {error_message}")
                return jsonify({
                    "status": "validation-error",
                    "message": error_message,
                }), 400  # Return 400 Bad Request for validation errors

            # Check if a prompt with the same content and user already exists
            existing_prompt = Prompt.query.filter_by(prompt=data['prompt'], user=data['user']).first()
            if existing_prompt:
                logger.info("Prompt with the same content already exists for this user.")
                return jsonify(existing_prompt.to_dict()), 200

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
                "timestamp": new_prompt.timestamp.isoformat()
            }), 200
        except Exception as e:
            db.session.rollback()
            logger.error(f"Unexpected error in prompt: {str(e)}")
            logger.error(traceback.format_exc())
            return jsonify({
                "error": "An unexpected error occurred",
                "details": str(e)
            }), 500

    def validateSchema(self, data):

        from server.app.utils.swagger_loader import SwaggerLoader

        validate(instance=data, schema=SwaggerLoader("swagger.yaml").get_component_schema("Prompt"))

    def delete_prompt_route(self, prompt_id:uuid):
        try:
            logger.info(f"Attempting to delete prompt with id: {prompt_id}")
            prompt = Prompt.query.get(prompt_id)
            if prompt:
                db.session.delete(prompt)
                db.session.commit()
                logger.info(f"Prompt with id {prompt_id} deleted successfully")
                return jsonify({"status": "Prompt deleted successfully"}), 200
            else:
                error_message = f"Prompt with id {prompt_id} not found"
                logger.warning(error_message)
                return jsonify({"error": error_message}), 404
        except Exception as e:
            logger.error(f"Error in prompt: {str(e)}")
            db.session.rollback()
            logger.error(traceback.format_exc())
            return jsonify({"error": str(e)}), 500

    def patch_prompt_route(self, prompt_id:uuid):
        try:
            data = request.json
            logger.info(f"Received prompt request with data: {data}")

            # Validate request data against the update prompt schema
            try:
                self.validateSchema(data)
                logger.info("Request data passed schema validation")
            except ValidationError as validation_error:
                error_message = validation_error.message
                logger.error(f"Validation error: {error_message}")
                return jsonify({
                    "status": "validation-error",
                    "message": error_message,
                }), 400

            # Find the prompt by id
            prompt = Prompt.query.get(prompt_id)
            if not prompt:
                logger.warning(f"Prompt with id {prompt_id} not found")
                return jsonify({"error": "Prompt not found"}), 404

            # Update the prompt
            prompt.prompt = data['prompt']
            prompt.user = data['user']
            prompt.status = data['status']  # Handle the status field
            db.session.commit()

            logger.info(f"Prompt updated successfully with id: {prompt_id}")
            return jsonify({
                "id": str(prompt_id),
                "prompt": prompt.prompt,
                "user": prompt.user,
                "status": prompt.status,  # Include status in response
                "timestamp": prompt.timestamp.isoformat()
            }), 200
        except Exception as e:
            db.session.rollback()
            logger.error(f"Unexpected error in prompt: {str(e)}")
            logger.error(traceback.format_exc())
            return jsonify({
                "error": "111An unexpected error occurred",
                "details": str(e)
            }), 500


prompts_controller = PromptsController()