from flask import Blueprint, request, Response, stream_with_context, jsonify
import asyncio
import json
import logging
from typing import List, Tuple, Any
import importlib
from server.app.config.base_config import BaseConfig
from server.app.clients.openai_client import OpenAIClient
from server.app.clients.anthropic_client import AnthropicClient
from .async_wrapper import AsyncWrapper

# Set up logging
logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)

class GenerationController:
    def __init__(self):
        self.blueprint = Blueprint('generation', __name__)
        self.register_routes()
        self.openai_client = OpenAIClient(api_key=BaseConfig.API_KEY_OPEN_AI)
        self.anthropic_client = AnthropicClient(api_key=BaseConfig.API_KEY_ANTHROPIC)
        self.registered_methods = ['fetch_completion', 'chat_completion', 'generate_image']
        self.clients = {
            'openai': self.openai_client,
            'anthropic': self.anthropic_client,
        }

    def register_routes(self):
        self.blueprint.add_url_rule('/stream', 'generate_route', self.stream_route, methods=['POST'])

    @staticmethod
    def get_model_class(platform):
        try:
            module = importlib.import_module(f"server.app.models.{platform}_model")
            return getattr(module, f"{platform.capitalize()}Model")
        except ImportError as e:
            logger.error(f"Error importing model module for platform '{platform}': {str(e)}")
        except AttributeError as e:
            logger.error(f"Error finding model class for platform '{platform}': {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error when getting model class for platform '{platform}': {str(e)}")
        return None

    def validate_models_and_clients(self, models: List[dict], method_name: str) -> List[Tuple[Any, Any, Any]]:
        valid_models = []
        for model_data in models:
            platform = model_data.get('platform')
            model_class = self.get_model_class(platform)
            if not model_class:
                raise ValueError(f"Model class for platform '{platform}' not found")

            platform_client = self.clients.get(platform)
            if not platform_client:
                raise ValueError(f"Client for platform '{platform}' not supported")

            if not hasattr(platform_client, method_name):
                raise ValueError(f"Method '{method_name}' not found for platform '{platform}'")

            valid_models.append((model_class(**model_data), platform_client, getattr(platform_client, method_name)))

        return valid_models

    def validate_request(self, models: List[dict], method_name: str, prompt_id: str):
        if not models:
            error_msg = "The 'models' list cannot be empty."
            logger.error(error_msg)
            raise ValueError(error_msg)

        if not prompt_id:
            error_msg = "The 'prompt_id' cannot be empty."
            logger.error(error_msg)
            raise ValueError(error_msg)

        if method_name not in self.registered_methods:
            error_msg = f"The method '{method_name}' is not allowed."
            logger.error(error_msg)
            raise ValueError(error_msg)

    def stream_route(self):
        logger.info("Incoming request to /stream:")
        logger.info(json.dumps(request.json, indent=2))
        logger.info("=" * 50)

        data = request.json
        models = data.get('models', [])
        prompt = data.get('prompt', '')
        prompt_id = data.get('prompt_id', '')
        method_name = data.get('method_name', 'fetch_completion')

        try:
            self.validate_request(models, method_name, prompt_id)
            valid_models = self.validate_models_and_clients(models, method_name)
        except ValueError as e:
            logger.error(str(e))
            return jsonify({"error": str(e)}), 400

        async def run_generation():
            for model, client, method in valid_models:
                try:
                    async for chunk in AsyncWrapper(method(model, prompt, prompt_id)):
                        yield chunk
                except Exception as e:
                    logger.error(f"Error during task execution for model {model.id}: {str(e)}")
                    yield json.dumps({"error": str(e)}).encode('utf-8') + b'\n'

        async def async_generator():
            async for chunk in run_generation():
                yield chunk

        return Response(stream_with_context(asyncio.run(async_generator())), content_type='application/json')

# Instantiate the GenerationController
generation_controller = GenerationController()