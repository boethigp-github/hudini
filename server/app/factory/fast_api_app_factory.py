from diskcache import FanoutCache
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from server.app.routers.models.models_router import router as models_router
from server.app.routers.prompts.prompts_router import router as prompts_router
from server.app.routers.generation.openai.openai_text_generation_router import router as generation_router
from server.app.routers.usercontext.usercontext_router import router as usercontext_router
from server.app.routers.generation.anthropic_generation_router import router as anthropic_generation_router
from server.app.routers.generation.google_ai_generation_router import router as google_ai_generation_router
from server.app.routers.socialmedia.telegram_router import router as socialmedia_telegram_router
from server.app.routers.generation.openai.openai_dalle3_image_generation_router import router as openai_dalle2_image_generation_router
from server.app.routers.socialmedia.telegram_image_text_router import router as socialmedia_telegram_image_text_router
from server.app.routers.users.users_router import router as users_router


class FastAPIAppFactory:
    def __init__(self, settings):
        self.logger = logging.getLogger("hudini_logger")
        self.logger.debug("FastAPIAppFactory: Set hudini_logger")
        self.settings = settings
        self.app = FastAPI(
            title="Hudini",
            description="""Hudini is a comprehensive API designed to facilitate interaction with various AI models, including those from OpenAI and Anthropic. 
            The API allows for seamless integration and management of AI-driven tasks such as text generation, image creation, and user context handling.
            """,
            version="1.0.0",
        )

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
            "http://localhost",  # For production, if served from the same domain
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
        self.app.include_router(usercontext_router)
        self.app.include_router(users_router)
        self.app.include_router(anthropic_generation_router)
        self.app.include_router(google_ai_generation_router)
        self.app.include_router(socialmedia_telegram_router)
        self.app.include_router(openai_dalle2_image_generation_router)
        self.app.include_router(socialmedia_telegram_image_text_router)
        self.logger.debug("Finished: Registering routes")

