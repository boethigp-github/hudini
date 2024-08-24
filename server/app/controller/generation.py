from flask import Blueprint, request, Response, stream_with_context, jsonify
import asyncio
from server.app.config.base_config import BaseConfig
from server.app.clients.openai_client import OpenAIClient

class GenerationController:
    def __init__(self):
        self.blueprint = Blueprint('generation', __name__)
        self.register_routes()
        self.openai_client = OpenAIClient(api_key=BaseConfig.OPENAI_API_KEY)

    def register_routes(self):
        self.blueprint.add_url_rule('/stream', 'generate_route', self.generate_route, methods=['POST'])

    def generate_route(self):
        data = request.json
        models = data.get('models', [])
        prompt = data.get('prompt', '')

        # Check if models list is empty and return a 400 response
        if not models:
            return jsonify({"error": "The 'models' list cannot be empty."}), 400

        def generate():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

            async def run_completions():
                tasks = []
                for model in models:
                    async_task = self.openai_client.fetch_completion(model, prompt)
                    task = asyncio.create_task(async_task)
                    tasks.append(task)

                for completed_task in asyncio.as_completed(tasks):
                    result = await completed_task
                    yield result  # Yield the serialized JSON result

            async def async_generator():
                async for item in run_completions():
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
