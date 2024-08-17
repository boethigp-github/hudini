import os
import logging
from flask import Flask
from flask_cors import CORS
from dotenv import load_dotenv
from app.routes.swagger import register_swagger_blueprints
from app.routes.models import models_blueprint
from app.routes.prompts import prompts_blueprint
from app.routes.generations import generations_blueprint
from app.config import Config
from flask_migrate import Migrate
from app.extensions import db

migrate = Migrate()
class FlaskAppFactory:
    def __init__(self):
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[logging.StreamHandler()]
        )
        self.logger = logging.getLogger(__name__)

    def find_and_load_dotenv(self, possible_paths):
        for path in possible_paths:
            if os.path.exists(path):
                load_dotenv(path)
                return path
        return None

    def load_config(self, app):
        app.config.from_object(Config)

    def register_blueprints(self, app):
        try:
            register_swagger_blueprints(app)
            app.register_blueprint(models_blueprint)
            app.register_blueprint(prompts_blueprint)
            app.register_blueprint(generations_blueprint)
            self.logger.info("Blueprints registered successfully.")
        except Exception as e:
            self.logger.exception(f"Error registering blueprints: {str(e)}")

    def create_app(self):
        self.logger.info("Starting application setup...")
        possible_env_paths = [
            os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '.env.local')),
            os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '.env.local')),
            os.path.abspath(os.path.join(os.getcwd(), '.env.local')),
            os.path.expanduser('~/.env.local'),
        ]

        env_path = self.find_and_load_dotenv(possible_env_paths)
        if env_path:
            self.logger.info(f".env.local file found and loaded from {env_path}")
        else:
            self.logger.error(f".env.local file not found in any of the possible locations: {possible_env_paths}")

        app = Flask(__name__)
        CORS(app, supports_credentials=True, resources={r"/*": {"origins": "http://localhost:5173"}})
        self.load_config(app)

        db.init_app(app)

        # Register blueprints
        self.register_blueprints(app)

        with app.app_context():
                db.create_all()  # This wil


        self.logger.info("Registered routes:")
        for rule in app.url_map.iter_rules():
            methods = ','.join(rule.methods)
            self.logger.info(f"{rule.endpoint}: {methods} {rule}")

        return app
