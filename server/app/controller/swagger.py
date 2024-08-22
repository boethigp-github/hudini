import logging
from flask import Blueprint,send_file, jsonify

logger = logging.getLogger(__name__)

class SwaggerController:
    """
    A controller class responsible for handling routes related to models.

    This class sets up the necessary routes to retrieve models from local storage and OpenAI,
    and handles requests for the favicon.
    """

    def __init__(self):
        """
        Initializes the SwaggerController instance.

        This method creates a Flask Blueprint for the models routes and registers the necessary routes.
        """
        # Create the blueprint for this controller
        self.blueprint = Blueprint('swagger', __name__)
        # Register the routes
        self.register_routes()

    def register_routes(self):
        """
        Registers routes to the Flask blueprint.

        This method maps the /get_models and /favicon.ico routes to their respective handler methods.
        """
        self.blueprint.add_url_rule('/swagger/yaml', 'swagger_yaml', self.swagger_yaml, methods=['GET'])

    @staticmethod
    def swagger_yaml():
        from server.app.utils.swagger_loader import SwaggerLoader
        yaml_file_path = SwaggerLoader("swagger.yaml").file_path()
        logger.debug(f"FilePath: {yaml_file_path}")

        return send_file(yaml_file_path, mimetype='application/x-yaml')

# Create an instance of the controller
swagger_controller = SwaggerController()
