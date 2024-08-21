import logging
from flask import Blueprint, jsonify, Response


# Set up logger for this module
logger = logging.getLogger(__name__)

class ModelsController:
    """
    A controller class responsible for handling routes related to models.

    This class sets up the necessary routes to retrieve models from local storage and OpenAI,
    and handles requests for the favicon.
    """

    def __init__(self):
        """
        Initializes the ModelsController instance.

        This method creates a Flask Blueprint for the models routes and registers the necessary routes.
        """
        # Create the blueprint for this controller
        self.blueprint = Blueprint('models', __name__)
        # Register the routes
        self.register_routes()

    def register_routes(self):
        """
        Registers routes to the Flask blueprint.

        This method maps the /get_models and /favicon.ico routes to their respective handler methods.
        """
        self.blueprint.add_url_rule('/get_models', 'get_models', self.get_models, methods=['GET'])
        self.blueprint.add_url_rule('/favicon.ico', 'favicon', self.favicon)

    @staticmethod
    def get_models():
        """
        Handles the /get_models route.

        This method retrieves available models from both local storage and OpenAI,
        and returns them as a JSON response.

        Returns:
            flask.Response: A JSON response containing lists of local and OpenAI models.
        """
        from server.app.config.base_config import BaseConfig
        from server.app.clients.llama_cpp_client import LLamaCppClient
        from server.app.clients.openai_client import OpenAIClient

        models_path =  BaseConfig.MODEL_PATH
        local_models = LLamaCppClient(models_path).get_available_models()
        openai_models = OpenAIClient(BaseConfig.OPENAI_API_KEY).get_available_models()
        logger.debug(f"Retrieved local models: {local_models}")
        logger.debug(f"Retrieved OpenAI models: {openai_models}")
        return jsonify({
            'local_models': local_models,
            'openai_models': openai_models
        })

    @staticmethod
    def favicon():
        """
        Handles the /favicon.ico route.

        This method returns a 204 No Content response for the favicon.ico request.

        Returns:
            flask.Response: An empty response with a 204 status code.
        """
        return Response(status=204)


# Create an instance of the controller
models_controller = ModelsController()
