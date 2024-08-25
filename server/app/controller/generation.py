from flask import Blueprint, request, Response, stream_with_context, jsonify
import asyncio
from server.app.config.base_config import BaseConfig
from server.app.clients.openai_client import OpenAIClient
from server.app.clients.anthropic_client import AnthropicClient

class GenerationController:
    def __init__(self):
        self.blueprint = Blueprint('generation', __name__)
        self.register_routes()
        self.openai_client = OpenAIClient(api_key=BaseConfig.API_KEY_OPEN_AI)
        self.anthropic_client = AnthropicClient(api_key=BaseConfig.API_KEY_OPEN_AI)
        self.registered_methods = ['fetch_completion', 'chat_completion', 'generate_image']

    def register_routes(self):
        self.blueprint.add_url_rule('/stream', 'generate_route', self.generate_route, methods=['POST'])

    def generate_route(self):
        data = request.json
        models = data.get('models', [])
        prompt = data.get('prompt', '')
        method_name = data.get('method_name', 'fetch_completion')

        # Check if models list is empty
        if not models:
            return jsonify({"error": "The 'models' list cannot be empty."}), 400

        # Check if the method_name is in the list of registered methods
        if method_name not in self.registered_methods:
            return jsonify({"error": f"The method '{method_name}' is not allowed."}), 400

        # Array of clients
        clients = [
            self.openai_client,
            # self.anthropic_client,
            # self.google_client,
            # self.llama_cpp_client,
            # self.ollama_client
        ]

        def generate():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

            async def run_generation():
                tasks = []
                for client in clients:
                    if hasattr(client, method_name):
                        method = getattr(client, method_name)
                        for model in models:
                            async_task = method(model, prompt)
                            task = asyncio.create_task(async_task)
                            tasks.append(task)
                    else:
                        print(f"Warning: Method '{method_name}' not found in {client.__class__.__name__}")

                for completed_task in asyncio.as_completed(tasks):
                    result = await completed_task
                    yield result  # Yield the serialized JSON result

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
                loop.close()

            yield from sync_generator()

        return Response(stream_with_context(generate()), content_type='application/json')

# Instantiate the GenerationController
generation_controller = GenerationController()
