# app/utils/app_factory.py

import os
import logging
from flask import Flask
from flask_cors import CORS
from dotenv import load_dotenv

from flask_migrate import Migrate




class FlaskAppFactory:
    def __init__(self):
        self.logger = self.setup_basic_logging()
        self.blueprints_registered=False

    @staticmethod
    def setup_basic_logging():
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[logging.StreamHandler()]
        )
        return logging.getLogger(__name__)

    @staticmethod
    def find_and_load_dotenv(possible_paths):
        for path in possible_paths:
            if os.path.exists(path):
                load_dotenv(path)
                return path
        return None

    def setup_logging(self, app):
        app.logger.setLevel(app.config.get('APP_LOG_LEVEL', 'DEBUG'))
        app.logger.debug(f"App {app.config.get('APP_PROJECT_NAME', 'Unknown')} starting.")
        app.logger.debug("Logging setup complete and working.")

    def create_app(self, config):
        app = Flask(__name__)

        CORS(app, supports_credentials=True, resources={r"/*": {"origins": "http://localhost:5173"}})

        app.config.from_object(config)



        self.load_environment(app)

        self.setup_logging(app)
        # Initialize extensions
        from ..extensions import db

        db.init_app(app)

        Migrate(app, db)

        from ..controller.models import models_controller
        app.register_blueprint(models_controller.blueprint)

        self.log_registered_routes(app)

        return app

    def register_blueprints(self, app):
        try:

            # from ..controller.swagger import register_swagger_blueprints
            # from ..controller.prompts import prompts_blueprint
            # from ..controller.generations import generations_blueprint

            # register_swagger_blueprints(app)
            #
            # app.register_blueprint(prompts_blueprint)
            # app.register_blueprint(generations_blueprint)
            self.logger.info("Blueprints registered successfully.")
        except Exception as e:
            self.logger.exception(f"Error registering blueprints: {str(e)}")

    def load_environment(self, app):
        possible_env_paths = [

            os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'infrastructure', 'environment','.env.local')),

        ]

        env_path = self.find_and_load_dotenv(possible_env_paths)
        if env_path:
            self.logger.info(f".env.local file found and loaded from {env_path}")
        else:
            self.logger.error(f".env.local file not found in any of the possible locations: {possible_env_paths}")

    def log_registered_routes(self, app):
        self.logger.info("Registered routes:")
        for rule in app.url_map.iter_rules():
            methods = ','.join(rule.methods)
            self.logger.info(f"{rule.endpoint}: {methods} {rule}")

