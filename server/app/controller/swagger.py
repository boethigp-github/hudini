from flask import Blueprint, send_file
from flask_swagger_ui import get_swaggerui_blueprint
import os

# Blueprint for serving the swagger.yaml file
swagger_blueprint = Blueprint('swagger', __name__)

@swagger_blueprint.route('/swagger.yaml')
def get_swagger_yaml():
    swagger_yaml_path = os.path.join(os.path.dirname(__file__), '..', '..', 'swagger.yaml')
    return send_file(swagger_yaml_path, mimetype='application/x-yaml')

# Configuration for Swagger UI
SWAGGER_URL = '/api/docs'  # URL for exposing Swagger UI (without trailing '/')
API_URL = '/swagger.yaml'  # Our API url (can of course be a local resource)

# Create Swagger UI blueprint
swaggerui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={
        'app_name': "Hudini API"
    }
)

# Function to register both blueprints
def register_swagger_blueprints(app):
    app.register_blueprint(swagger_blueprint)
    app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)

# Note: Call register_swagger_blueprints(app) in your main app file
