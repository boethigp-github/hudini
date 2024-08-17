import os
import logging
from flask import Flask
from flask_cors import CORS
from dotenv import load_dotenv
from app.routes.swagger import register_swagger_blueprints  # Import the registration function
from app.routes.models import models_blueprint
from app.routes.prompts import prompts_blueprint
from app.routes.generations import generations_blueprint
from app.config import Config

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)

logger = logging.getLogger(__name__)

def find_and_load_dotenv(possible_paths):
    for path in possible_paths:
        if os.path.exists(path):
            load_dotenv(path)
            return path
    return None

def create_app():
    logger.info("Starting application setup...")

    possible_env_paths = [
        os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '.env.local')),
        os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '.env.local')),
        os.path.abspath(os.path.join(os.getcwd(), '.env.local')),
        os.path.expanduser('~/.env.local'),
    ]

    env_path = find_and_load_dotenv(possible_env_paths)

    if env_path:
        logger.info(f".env.local file found and loaded from {env_path}")
    else:
        logger.error(f".env.local file not found in any of the possible locations: {possible_env_paths}")

    app = Flask(__name__)

    CORS(app, supports_credentials=True, resources={r"/*": {"origins": "http://localhost:5173"}})

    app.config.from_object(Config)

    # Register Swagger blueprints
    register_swagger_blueprints(app)

    # Register other blueprints
    app.register_blueprint(models_blueprint)
    app.register_blueprint(prompts_blueprint)
    app.register_blueprint(generations_blueprint)

    logger.info("Registered routes:")
    for rule in app.url_map.iter_rules():
        methods = ','.join(rule.methods)
        logger.info(f"{rule.endpoint}: {methods} {rule}")

    return app
