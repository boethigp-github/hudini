from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, AsyncEngine
from sqlalchemy.orm import sessionmaker, declarative_base
from aiocache import Cache
from aiocache.serializers import JsonSerializer
from alembic.config import Config
from alembic import command
from concurrent.futures import ThreadPoolExecutor
import os
import asyncio
import logging.config  # Import this to apply logging config from a dictionary


class FastAPIAppFactory:
    def __init__(self):
        self.app = None
        self.logger = None
        self.Base = declarative_base()  # Define the Base here

    def create_app(self, config):
        # Set up logging using the configuration from the loaded settings object
        logging_config = config.get('default__LOGGING_CONFIG')
        self.setup_logging(logging_config)
        self.logger = logging.getLogger(__name__)

        # Initialize the FastAPI app using values from the settings object
        self.app = FastAPI(title=config.get('default__APP_PROJECT_NAME'), version="1.0.0")
        self.load_config(config)
        self.set_cors(config.get('default__CORS_ORIGINS').split(','))
        self.initialize_cache()
        self.init_database(config.get('default__DATABASE_URL'))
        self.register_routes()  # Register routes after initializing the database
        return self.app

    def setup_logging(self, logging_config):
        """Set up logging configuration from the provided config."""
        logging.config.dictConfig(logging_config)

    def load_config(self, config):
        for key, value in config.config['default'].items():  # Use the raw config dictionary
            setattr(self.app.state, key, value)

    def set_cors(self, origins):
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=origins,
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

    def initialize_cache(self):
        cache = Cache(Cache.MEMORY, serializer=JsonSerializer())
        self.app.state.cache = cache

    def init_database(self, database_url):
        """Initialize database connection and run migrations."""
        engine: AsyncEngine = create_async_engine(database_url, echo=True)
        async_session: sessionmaker = sessionmaker(
            engine,
            class_=AsyncSession,
            expire_on_commit=False
        )
        self.app.state.db = async_session

        # Create the tables if not using migrations
        async def create_tables():
            async with engine.begin() as conn:
                await conn.run_sync(self.Base.metadata.create_all)

        # Run table creation in the event loop
        asyncio.run(create_tables())

        # Run migrations in a separate thread if needed
        with ThreadPoolExecutor() as pool:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_in_executor(pool, self.run_migrations)

    def run_migrations(self):
        """Run migrations using Alembic. This should be called outside of the async context."""
        # Resolve the path to alembic.ini
        alembic_path = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'alembic.ini')
        alembic_cfg = Config(alembic_path)

        # Run migrations
        command.upgrade(alembic_cfg, "head")

    def register_routes(self):
        from server.app.controller.swagger_ui import SwaggerUiController
        from server.app.controller.models import ModelsController
        from server.app.controller.generation import GenerationController
        from server.app.controller.prompts import PromptsController

        # Initialize controllers with the logger
        swagger_ui_controller = SwaggerUiController(self.logger)
        models_controller = ModelsController(self.logger)
        generation_controller = GenerationController(self.app.state.db, self.logger)
        prompts_controller = PromptsController(self.app.state.db, self.logger)

        self.app.include_router(swagger_ui_controller.router)
        self.app.include_router(models_controller.router)
        self.app.include_router(generation_controller.router)
        self.app.include_router(prompts_controller.router)
