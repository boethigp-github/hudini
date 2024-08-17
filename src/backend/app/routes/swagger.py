from flask import Blueprint, send_file
import os

swagger_blueprint = Blueprint('swagger', __name__)

@swagger_blueprint.route('/swagger.yaml')
def get_swagger_yaml():
    swagger_yaml_path = os.path.join(os.path.dirname(__file__), '..', '..', 'swagger.yaml')
    return send_file(swagger_yaml_path, mimetype='application/x-yaml')
