from flask import Blueprint, request, Response, stream_with_context
import logging
import json
import asyncio
from openai import AsyncOpenAI
from server.app.config.base_config import  BaseConfig

class GenerationController:
    def __init__(self):
        self.blueprint = Blueprint('generation', __name__)
        self.register_routes()
        self.logger = self.setup_logger()
        self.openai_client = AsyncOpenAI(api_key=BaseConfig.OPENAI_API_KEY)

    def setup_logger(self):
        logger = logging.getLogger(__name__)
        logger.setLevel(logging.DEBUG)
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        return logger

    def register_routes(self):
        self.blueprint.add_url_rule('/stream', 'generate_route', self.generate_route, methods=['POST'])

    async def fetch_completion(self, model, prompt):
        try:
            completion = await self.openai_client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.0
            )
            return {
                'model': model,
                'completion': completion.to_dict()
            }
        except Exception as e:
            self.logger.error(f"Error with model {model}: {str(e)}")
            return {
                'model': model,
                'error': str(e)
            }

    def generate_route(self):
        data = request.json
        models = data.get('models', [])
        prompt = data.get('prompt', '')

        def generate():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

            async def run_completions():
                tasks = [asyncio.create_task(self.fetch_completion(model, prompt)) for model in models]
                for completed_task in asyncio.as_completed(tasks):
                    result = await completed_task
                    yield json.dumps(result) + '\n'

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

generation_controller = GenerationController()