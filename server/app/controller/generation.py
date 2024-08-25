from flask import Blueprint, request, Response, stream_with_context, jsonify
import asyncio
import json
import logging
from server.app.config.base_config import BaseConfig
from server.app.clients.openai_client import OpenAIClient
from server.app.clients.anthropic_client import AnthropicClient
import importlib

# Set up logging
logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)

def get_model_class(platform):
    try:
        module_name = f"server.app.models.{platform}_model"
        module = importlib.import_module(module_name)
        class_name = f"{platform.capitalize()}Model"
        model_class = getattr(module, class_name)
        return model_class
    except ImportError as e:
        logger.error(f"Error importing model module for platform '{platform}': {str(e)}")
    except AttributeError as e:
        logger.error(f"Error finding model class for platform '{platform}': {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error when getting model class for platform '{platform}': {str(e)}")
    return None

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
        self.blueprint.add_url_rule('/stream', 'generate_route', self.generate_route, methods=['POST'])

    def generate_route(self):
        # Log the incoming request
        logger.info("Incoming request to /stream:")
        logger.info(json.dumps(request.json, indent=2))
        logger.info("=" * 50)  # Separator for clarity in logs

        data = request.json
        models = data.get('models', [])
        prompt = data.get('prompt', '')
        method_name = data.get('method_name', 'fetch_completion')

        if not models:
            error_msg = "The 'models' list cannot be empty."
            logger.error(error_msg)
            return jsonify({"error": error_msg}), 400

        if method_name not in self.registered_methods:
            error_msg = f"The method '{method_name}' is not allowed."
            logger.error(error_msg)
            return jsonify({"error": error_msg}), 400

        # Validate models and clients before starting the generator
        valid_models = []
        for model_data in models:
            platform = model_data.get('platform')
            model_class = get_model_class(platform)
            if not model_class:
                error_msg = f"Model class for platform '{platform}' not found"
                logger.error(error_msg)
                return jsonify({"error": error_msg}), 400

            platform_client = self.clients.get(platform)
            if not platform_client:
                error_msg = f"Client for platform '{platform}' not supported"
                logger.error(error_msg)
                return jsonify({"error": error_msg}), 400

            if not hasattr(platform_client, method_name):
                error_msg = f"Method '{method_name}' not found for platform '{platform}'"
                logger.error(error_msg)
                return jsonify({"error": error_msg}), 400

            valid_models.append((model_class(**model_data), platform_client, getattr(platform_client, method_name)))

        def generate():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

            async def run_generation():
                tasks = []
                for model, client, method in valid_models:
                    async_task = method(model, prompt)
                    task = asyncio.create_task(async_task)
                    tasks.append(task)

                for completed_task in asyncio.as_completed(tasks):
                    try:
                        result = await completed_task
                        yield result  # Yield the serialized JSON result
                    except Exception as e:
                        logger.error(f"Error during task execution: {str(e)}")
                        yield json.dumps({"error": str(e)})

            async def async_generator():
                async for item in run_generation():
                    yield item

            def sync_generator():
                async_gen = async_generator()
                while True:
                    try:
                        yield loop.run_until_complete(async_gen.__anext__())
                    except StopAsyncIteration:
                        break
                    except Exception as e:
                        logger.error(f"Error in sync_generator: {str(e)}")
                        yield json.dumps({"error": str(e)})
                loop.close()

            yield from sync_generator()

        return Response(stream_with_context(generate()), content_type='application/json')

# Instantiate the GenerationController
generation_controller = GenerationController()