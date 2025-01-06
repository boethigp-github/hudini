import logging
from diskcache import FanoutCache
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware as FastAPISessionMiddleware

from server.app.routers.models.models_router import router as models_router
from server.app.routers.prompts.prompts_router import router as prompts_router
from server.app.routers.generation.cerebras.cerebras_text_generation_router import router as cerebras_generation_router
from server.app.routers.generation.openai.openai_text_generation_router import router as open_ai_text_generation_router
from server.app.routers.usercontext.usercontext_router import router as usercontext_router
from server.app.routers.generation.anthropic_generation_router import router as anthropic_generation_router
from server.app.routers.generation.google_ai_generation_router import router as google_ai_generation_router
from server.app.routers.socialmedia.telegram_router import router as socialmedia_telegram_router
from server.app.routers.generation.openai.openai_dalle3_image_generation_router import router as openai_dalle2_image_generation_router
from server.app.routers.socialmedia.telegram_image_text_router import router as socialmedia_telegram_image_text_router
from server.app.routers.tool.calling_router import router as tool_call_router
from server.app.routers.gripsbox.gripsbox_router import router as gripsbox_router
from server.app.routers.models_parameter.models_parameter_router import router as models_parameter_router
from server.app.routers.users.users_router import router as users_router
from server.app.routers.postcasts.google.podcast_google_tts_router import router as podcast_google_tts_router
from server.app.routers.postcasts.elevenlabs.podcast_elevenlabs_router import router as podcast_elevenlabs_router
from server.app.routers.auth.auth_router import router as auth_router, setup_oauth

logger = logging.getLogger("hudini_logger")



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
        self.initialize_oauth()
        self.add_cors_middleware()
        self.add_session_middleware()  # FastAPI session middleware (built-in) - now last
        self.register_routes()
        return self.app

    def load_config(self, config):
        for key, value in config.items():
            setattr(self.app.state, key, value)

    def initialize_cache(self):
        self.logger.debug("Initializing FanoutCache")
        cache_directory = self.settings.get("default").get("APP_CACHE")
        self.logger.debug(f"Cache directory set to: {cache_directory}")
        cache = FanoutCache(directory=cache_directory, shards=8)
        self.app.state.cache = cache

    def add_session_middleware(self):
        self.logger.debug("Adding FastAPISessionMiddleware")
        secret_key = self.settings.get("default").get("APP_GOOGLE_AUTH_CLIENT_SECRET")
        if not secret_key:
            self.logger.error("No APP_GOOGLE_AUTH_CLIENT_SECRET found. SessionMiddleware cannot be added.")
            raise ValueError("APP_GOOGLE_AUTH_CLIENT_SECRET is required for SessionMiddleware")

        # Add FastAPI session middleware to manage sessions
        self.app.add_middleware(
            FastAPISessionMiddleware,
            secret_key=secret_key,
            session_cookie="session",
            max_age=3600,  # 1-hour session expiration
            same_site="lax",  # For security reasons
            https_only=False  # Set to True in production
        )

    def add_custom_session_protection_middleware(self):
        self.logger.debug("Adding custom session protection middleware")


    def initialize_oauth(self):
        self.logger.debug("Initializing OAuth")
        setup_oauth()

    def add_cors_middleware(self):
        self.logger.debug("Adding CORS middleware")
        origins = self.settings.get("default").get("APP_CORS_ORIGIN", "").split(",")
        if not origins:
            self.logger.warning("No CORS origins specified. Allowing all origins.")
            origins = ["*"]

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
        self.app.include_router(cerebras_generation_router)
        self.app.include_router(usercontext_router)
        self.app.include_router(users_router)
        self.app.include_router(anthropic_generation_router)
        self.app.include_router(google_ai_generation_router)
        self.app.include_router(socialmedia_telegram_router)
        self.app.include_router(openai_dalle2_image_generation_router)
        self.app.include_router(socialmedia_telegram_image_text_router)
        self.app.include_router(gripsbox_router)
        self.app.include_router(auth_router)
        self.app.include_router(tool_call_router)
        self.app.include_router(tool_call_router)
        self.app.include_router(open_ai_text_generation_router)
        self.app.include_router(models_parameter_router)
        self.app.include_router(models_parameter_router)
        self.app.include_router(podcast_elevenlabs_router)
        self.app.include_router(podcast_google_tts_router)
        self.logger.debug("Finished: Registering routes")