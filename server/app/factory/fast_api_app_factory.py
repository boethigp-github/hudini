import asyncio
from fastapi import FastAPI
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, AsyncEngine
from sqlalchemy.orm import sessionmaker, declarative_base
from aiocache import Cache
from aiocache.serializers import JsonSerializer
from alembic.config import Config
from alembic import command
import os
from fastapi.middleware.cors import CORSMiddleware
from ..utils.hudini_logger import hudini_logger  # Import the global hudini_logger
from ..routers.swagger_ui_router import router as swagger_ui_router
from ..routers.models_router import router as models_router
class FastAPIAppFactory:
    def __init__(self, settings):

        self.logger = hudini_logger  # Use the global hudini_logger

        self.logger.debug("FastAPIAppFactory: Set hudini_logger")
        self.settings = settings
        self.app = FastAPI()

    def create_app(self):
        self.logger.debug("Creating FastAPI application")
        # self.logger.debug("Logging all configuration items:")
        # self.log_all_config_items(self.settings)
        #
        # database_url = self.resolve_config_value(self.settings.get('default', {}).get('DATABASE_URL'))
        # if not database_url:
        #     self.logger.error("DATABASE_URL is missing in settings")
        #     raise ValueError("DATABASE_URL must be provided in the settings.")

        self.initialize_cache()
        self.register_routes()
        return self.app

    def log_all_config_items(self, config):
        for key, value in config.items():
            resolved_value = self.resolve_config_value(value)
            self.logger.debug(f"{key}: {resolved_value} (type: {type(resolved_value).__name__})")

    def resolve_config_value(self, value):
        if isinstance(value, str) and "${" in value:
            import re
            pattern = re.compile(r'\$\{([^}]+)\}')
            matches = pattern.findall(value)
            for match in matches:
                env_var, _, default = match.partition(':')
                value = value.replace(f"${{{match}}}", os.getenv(env_var, default))
        elif isinstance(value, dict):
            return {k: self.resolve_config_value(v) for k, v in value.items()}
        return value

    def load_config(self, config):
        for key, value in config.items():
            setattr(self.app.state, key, value)

    def initialize_cache(self):
        self.logger.debug("Initializing cache")
        cache = Cache(Cache.MEMORY, serializer=JsonSerializer())
        self.app.state.cache = cache

     # def init_database(self, database_url):
     #    self.logger.debug("Initializing database connection")
        # engine: AsyncEngine = create_async_engine(database_url, echo=True)
        # async_session: sessionmaker = sessionmaker(
        #     engine,
        #     class_=AsyncSession,
        #     expire_on_commit=False
        # )
        # self.app.state.db = async_session

    #     async def create_tables():
    #         self.logger.debug("Starting to create tables")
    #         async with engine.begin() as conn:
    #             await conn.run_sync(self.Base.metadata.create_all)
    #         self.logger.debug("Tables created successfully")
    #
    #     await create_tables()
    #     self.logger.debug("Database table creation completed")
    #
    #     loop = asyncio.get_event_loop()
    #     await loop.run_in_executor(None, self.run_migrations)
    #     self.logger.debug("Database migrations completed")
    #
    # def run_migrations(self):
    #     self.logger.debug("Starting Alembic migrations")
    #     alembic_path = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'infrastructure', 'database', 'alembic.ini')
    #     alembic_cfg = Config(alembic_path)
    #     self.logger.debug(f"Using Alembic configuration file at: {alembic_path}")
    #     command.upgrade(alembic_cfg, "head")
    #     self.logger.debug("Alembic migrations applied successfully")

    def register_routes(self):
        self.logger.debug("Registering routes")
        self.app.include_router(swagger_ui_router)
        self.app.include_router(models_router)


