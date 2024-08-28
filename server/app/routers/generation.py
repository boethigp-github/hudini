from fastapi import APIRouter, HTTPException, Request, Depends
from fastapi.responses import StreamingResponse
import asyncio
import json
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Dict, Any
import importlib
from ..config.settings import Settings
from ..clients.openai_client import OpenAIClient
from ..clients.anthropic_client import AnthropicClient
from sqlalchemy.orm import sessionmaker


class GenerationController:
    def __init__(self, async_session: sessionmaker, app_logger):
        self.router = APIRouter()
        self.async_session = async_session
        self.logger = app_logger  # Use the logger passed from FastAPIAppFactory

        # Initialize the Settings instance
        self.settings = Settings()

        # Use the API keys from Settings instead of BaseConfig
        self.openai_client = OpenAIClient(api_key=self.settings.API_KEY_OPEN_AI)
        self.anthropic_client = AnthropicClient(api_key=self.settings.api_key_anthropic)

        self.registered_methods = ['fetch_completion', 'chat_completion', 'generate_image']
        self.clients = {
            'openai': self.openai_client,
            'anthropic': self.anthropic_client,
        }
        self.register_routes()

    def register_routes(self):
        self.router.add_api_route("/stream", self.stream_route, methods=["POST"])

    def get_model_class(self, platform):
        try:
            module = importlib.import_module(f"..models.{platform}_model")
            return getattr(module, f"{platform.capitalize()}Model")
        except ImportError as e:
            self.logger.error(f"Error importing model module for platform '{platform}': {str(e)}")
        except AttributeError as e:
            self.logger.error(f"Error finding model class for platform '{platform}': {str(e)}")
        except Exception as e:
            self.logger.error(f"Unexpected error when getting model class for platform '{platform}': {str(e)}")
        return None

    def validate_models_and_clients(self, models: List[dict], method_name: str) -> List[Any]:
        valid_models = []
        for model_data in models:
            platform = model_data.get('platform')
            model_class = self.get_model_class(platform)
            if not model_class:
                raise HTTPException(status_code=400, detail=f"Model class for platform '{platform}' not found")

            platform_client = self.clients.get(platform)
            if not platform_client:
                raise HTTPException(status_code=400, detail=f"Client for platform '{platform}' not supported")

            if not hasattr(platform_client, method_name):
                raise HTTPException(status_code=400,
                                    detail=f"Method '{method_name}' not found for platform '{platform}'")

            valid_models.append((model_class(**model_data), platform_client, getattr(platform_client, method_name)))

        return valid_models

    def validate_request(self, models: List[dict], method_name: str, prompt_id: str):
        if not models:
            raise HTTPException(status_code=400, detail="The 'models' list cannot be empty.")

        if not prompt_id:
            raise HTTPException(status_code=400, detail="The 'prompt_id' cannot be empty.")

        if method_name not in self.registered_methods:
            raise HTTPException(status_code=400, detail=f"The method '{method_name}' is not allowed.")

    async def stream_route(self, request: Request, db: AsyncSession = Depends()):
        data = await request.json()
        self.logger.info("Incoming request to /stream:")
        self.logger.info(json.dumps(data, indent=2))
        self.logger.info("=" * 50)

        models = data.get('models', [])
        prompt = data.get('prompt', '')
        prompt_id = data.get('prompt_id', '')
        method_name = data.get('method_name', 'fetch_completion')

        try:
            self.validate_request(models, method_name, prompt_id)
            valid_models = self.validate_models_and_clients(models, method_name)
        except HTTPException as e:
            self.logger.error(str(e))
            raise e

        async def generate():
            tasks = []
            for model, client, method in valid_models:
                async_task = method(model, prompt, prompt_id)
                task = asyncio.create_task(async_task)
                tasks.append(task)

            for completed_task in asyncio.as_completed(tasks):
                try:
                    async_gen = await completed_task
                    async for result in async_gen:
                        yield result  # Result is already in bytes
                except Exception as e:
                    self.logger.error(f"Error during task execution: {str(e)}")
                    yield json.dumps({"error": str(e)}).encode('utf-8') + b'\n'

        return StreamingResponse(generate(), media_type='application/json')
