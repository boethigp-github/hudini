import os
import logging
from flask import Flask, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
from flask_migrate import Migrate
from server.app.extensions import cache


class FlaskAppFactory:
    def __init__(self):
        self.logger = self.setup_basic_logging()
        self.blueprints_registered = False
        self.app = None

    def create_app(self, config):
        return (
            self.initialize_app(config)
            .load_environment()
            .setup_logging()
            .set_cors()
            .initialize_cache()
            .register_commands()
            .init_database()
            .register_route_controller()
            .app
        )

    def initialize_app(self, config):
        """Initialize the Flask app """
        self.app = Flask(__name__)  # Initialize the app first
        self.app.config.from_object(config)  # Then configure it
        return self

    def set_cors(self):
        """Initialize CORS."""
        origins = self.app.config.get("CORS_ORIGINS", ["http://localhost:5173"])  # Default if not set
        CORS(self.app, supports_credentials=True, resources={r"/*": {"origins": origins}})
        return self

    def load_environment(self):
        """Load environment variables."""
        possible_env_paths = [
            os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'infrastructure', 'environment', '.env.local')),
        ]

        env_path = FlaskAppFactory.find_and_load_dotenv(possible_env_paths)
        if env_path:
            logging.getLogger(__name__).info(f".env.local file found and loaded from {env_path}")
        else:
            logging.getLogger(__name__).error(f".env.local file not found in any of the possible locations: {possible_env_paths}")
        return self

    def setup_logging(self):
        """Set up logging for the Flask app."""
        self.app.logger.setLevel(self.app.config.get('APP_LOG_LEVEL', 'DEBUG'))
        self.app.logger.debug(f"App {self.app.config.get('APP_PROJECT_NAME', 'Unknown')} starting.")
        self.app.logger.debug("Logging setup complete and working.")
        return self

    def initialize_cache(self):
        """Initialize the cache."""
        cache.init_cache(self.app)
        return self

    def register_commands(self):
        """Register CLI commands."""
        from server.app.cli.cache_clear import cache_clear
        self.app.cli.add_command(cache_clear)
        return self

    def init_database(self):
        """Initialize extensions like the database and migrations."""
        from ..extensions import db
        db.init_app(self.app)
        Migrate(self.app, db)
        return self

    def register_route_controller(self):
        """Register Flask blueprints."""

        from ..controller.models import models_controller
        self.app.register_blueprint(models_controller.blueprint)

        from ..controller.swagger import swagger_controller
        self.app.register_blueprint(swagger_controller.blueprint)

        from ..controller.prompts import prompts_controller
        self.app.register_blueprint(prompts_controller.blueprint)

        from ..controller.generation import generation_controller
        self.app.register_blueprint(generation_controller.blueprint)

        return self




    @staticmethod
    def find_and_load_dotenv(possible_paths):
        """Find and load environment variables from a .env file."""
        for path in possible_paths:
            if os.path.exists(path):
                load_dotenv(path)
                return path
        return None

    @staticmethod
    def setup_basic_logging():
        """Set up basic logging."""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[logging.StreamHandler()]
        )


        return logging.getLogger(__name__)

    @staticmethod
    def register_error_handlers(app):
        """Register global error handlers."""
        @app.errorhandler(Exception)
        def handle_exception(e):
            app.logger.exception('An unhandled exception occurred')
            response = jsonify({'error': str(e)})
            response.status_code = 500
            return response
