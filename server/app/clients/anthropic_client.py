import logging
import anthropic
from anthropic import AsyncAnthropic
from server.app.models.success_generation_model import SuccessGenerationModel
from server.app.models.generation_error_details import ErrorGenerationModel
from server.app.models.anthropic_model import AnthropicModel

class AnthropicClient:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.client = AsyncAnthropic(api_key=api_key)  # For async operations
        self.sync_client = anthropic.Anthropic(api_key=api_key)  # For synchronous operations
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

    async def fetch_completion(self, model: AnthropicModel, prompt: str) -> str:
        try:
            self.logger.debug(f"Fetching completion for model: {model.id}")
            message = await self.client.messages.create(
                model=model.id,
                max_tokens=1000,
                temperature=0,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )

            return SuccessGenerationModel(
                model=model.id,
                completion=message.model_dump()
            ).model_dump_json()

        except Exception as e:
            self.logger.error(f"Error with model {model.id}: {str(e)}")
            return ErrorGenerationModel(
                model=model.id,
                error=str(e)
            ).model_dump_json()

    def get_available_models(self) -> list:
        """
        Returns the list of available models from Anthropic.

        Returns:
            list: A list of AnthropicModel instances representing the models available in the Anthropic API.
        """
        try:
            models = [
                AnthropicModel(id="claude-3-5-sonnet-20240620", created=None, platform="anthropic"),
                AnthropicModel(id="claude-3-opus-20240229", created=None, platform="anthropic"),
                AnthropicModel(id="claude-3-sonnet-20240229", created=None, platform="anthropic"),
                AnthropicModel(id="claude-3-haiku-20240307", created=None, platform="anthropic")
            ]

            self.logger.debug(f"Retrieved {len(models)} models from Anthropic")
            return [model.model_dump() for model in models]
        except Exception as e:
            self.logger.error(f"Failed to fetch models from Anthropic: {str(e)}", exc_info=True)
            raise ValueError(f"Error fetching models from Anthropic: {str(e)}")