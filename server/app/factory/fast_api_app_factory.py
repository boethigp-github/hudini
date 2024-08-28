from fastapi import FastAPI
from aiocache import Cache
from aiocache.serializers import JsonSerializer
import os
from ..utils.hudini_logger import hudini_logger
from ..routers.models_router import router as models_router
class FastAPIAppFactory:
    def __init__(self, settings):
        self.logger = hudini_logger
        self.logger.debug("FastAPIAppFactory: Set hudini_logger")
        self.settings = settings
        self.app = FastAPI()

    def create_app(self):
        self.logger.debug("Creating FastAPI application")
        self.initialize_cache()
        self.register_routes()
        return self.app


    def load_config(self, config):
        for key, value in config.items():
            setattr(self.app.state, key, value)

    def initialize_cache(self):
        self.logger.debug("Initializing cache")
        cache = Cache(Cache.MEMORY, serializer=JsonSerializer())
        self.app.state.cache = cache


    def register_routes(self):
        self.logger.debug("Registering routes")
        self.app.include_router(models_router)
        self.logger.debug("Finished: Registering routes")


