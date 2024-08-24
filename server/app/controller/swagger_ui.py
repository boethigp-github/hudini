import logging
from flask import Blueprint, send_file, redirect
from flask_swagger_ui import get_swaggerui_blueprint
from server.app.utils.swagger_loader import SwaggerLoader

logger = logging.getLogger(__name__)

class SwaggerUiController:
    """
    A controller class responsible for handling routes related to the Swagger UI and YAML file.
    """

    def __init__(self):
        """
        Initializes the SwaggerUiController instance.

        This method creates Flask Blueprints for serving the swagger.yaml file and the Swagger UI.
        """
        # Create the blueprint for serving the swagger.yaml file and handling redirects
        self.blueprint = Blueprint('swagger_ui_endpoint', __name__)

        # Create Swagger UI blueprint, which will be served at /api/docs
        self.swagger_ui_blueprint = get_swaggerui_blueprint(
            '/api/docs',
            '/swagger.yaml',
            config={
                'app_name': "Hudini API"
            }
        )

        # Register the routes for serving the swagger.yaml file and root redirect
        self.register_routes()

    def register_routes(self):
        """
        Registers routes to the Flask blueprint.
        """
        # Serve swagger.yaml file at /swagger.yaml
        self.blueprint.add_url_rule('/swagger.yaml', 'swagger_yaml', self.serve_swagger_yaml, methods=['GET'])

        # Redirect from / to /api/docs
        self.blueprint.add_url_rule('/', 'redirect_to_docs', self.redirect_to_docs, methods=['GET'])

    def serve_swagger_yaml(self):
        """
        Handler method for serving the swagger.yaml file.
        """
        swagger_loader = SwaggerLoader("swagger.yaml")
        logger.debug(f"Serving swagger.yaml from path: {swagger_loader.file_path()}")
        return send_file(swagger_loader.file_path(), mimetype='application/x-yaml')

    def redirect_to_docs(self):
        """
        Redirects requests from the root URL (/) to /api/docs.
        """
        return redirect('/api/docs')  # Directly redirect to the Swagger UI path

# Create an instance of the controller
swagger_ui_controller = SwaggerUiController()
