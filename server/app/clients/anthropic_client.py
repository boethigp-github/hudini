import logging
import json
from anthropic import AsyncAnthropic

from server.app.models.anthropic_model import AnthropicModel

class AnthropicClient:
    async_methods = ['fetch_completion']

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.client = AsyncAnthropic(api_key=api_key)
        self.logger = self.setup_logger()
        self.logger.debug(f"AnthropicClient initialized with API key: {api_key[:5]}...")

    def setup_logger(self):
        logger = logging.getLogger(__name__)
        logger.setLevel(logging.DEBUG)
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        return logger

    async def fetch_completion(self, model: AnthropicModel, prompt: str, prompt_id: str):
        try:
            self.logger.error(f"Antropic called: {model.id}")
            async with self.client.messages.stream(
                max_tokens=1024,
                messages=[
                    {
                        "role": "user",
                        "content": prompt,
                    }
                ],
                model=model.id,
            ) as stream:
                async for text in stream.text_stream:
                    yield text.encode('utf-8')
                yield b'\n'  # Add a newline after the stream ends

            message = await stream.get_final_message()
            yield json.dumps(message.to_dict()).encode('utf-8')
        except Exception as e:
            self.logger.error(f"Error with model {model.id}: {str(e)}")
            yield json.dumps({"error": str(e)}).encode('utf-8') + b'\n'

    def get_available_models(self) -> list:
        """
        Returns the list of available models from Anthropic.

        Returns:
            list: A list of AnthropicModel instances representing the models available in the Anthropic API.
        """
        try:
            models = [
                AnthropicModel(id="claude-3-5-sonnet-20240620", created=None, platform="anthropic", category='text_completion'),
                AnthropicModel(id="claude-3-opus-20240229", created=None, platform="anthropic", category='embedding'),
                AnthropicModel(id="claude-3-sonnet-20240229", created=None, platform="anthropic", category='text_completion'),
                AnthropicModel(id="claude-3-haiku-20240307", created=None, platform="anthropic", category='text_completion')
            ]

            self.logger.debug(f"Retrieved {len(models)} models from Anthropic")
            return [model.model_dump() for model in models]
        except Exception as e:
            self.logger.error(f"AnthropicClient::get_available_models: Failed to fetch models from Anthropic: {str(e)}", exc_info=True)
            raise ValueError(f"AnthropicClient::get_available_models: Error fetching models from Anthropic: {str(e)}")