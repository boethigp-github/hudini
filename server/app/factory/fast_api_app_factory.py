from diskcache import FanoutCache
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
from ..utils.hudini_logger import hudini_logger
from ..routers.models_router import router as models_router
from ..routers.prompts_router import router as prompts_router
from ..routers.generation_router import router as generation_router

class FastAPIAppFactory:
    def __init__(self, settings):
        self.logger = logging.getLogger("hudini_logger")
        self.logger.debug("FastAPIAppFactory: Set hudini_logger")
        self.settings = settings
        self.app = FastAPI()

    def create_app(self):
        self.logger.debug("Creating FastAPI application")
        self.initialize_cache()
        self.add_cors_middleware()
        self.register_routes()
        return self.app

    def load_config(self, config):
        for key, value in config.items():
            setattr(self.app.state, key, value)

    def initialize_cache(self):
        self.logger.debug("Initializing FanoutCache")
        # Set up FanoutCache with persistent storage in a specified directory
        cache_directory = self.settings.get("default").get("APP_CACHE")  # Replace with your actual directory
        self.logger.debug(f"Cache directory set to: {cache_directory}")
        cache = FanoutCache(directory=cache_directory, shards=8)
        self.app.state.cache = cache

    def add_cors_middleware(self):
        self.logger.debug("Adding CORS middleware")
        origins = [
            "http://localhost:5173",  # Your Vue.js development server
            "http://localhost:8080",  # Another common development port
            "http://localhost",       # For production, if served from the same domain
            # Add any other origins you need to allow
        ]

        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=origins,
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

    def register_routes(self):
        self.logger.debug("Registering routes")
        self.app.include_router(models_router)
        self.app.include_router(prompts_router)
        self.app.include_router(generation_router)
        self.logger.debug("Finished: Registering routes")
