import logging
from typing import AsyncIterable, Optional
from server.app.models.generation.success_generation_model import SuccessGenerationModel, Completion, Choice, Message, Usage
from ..models.anthropic_model import AnthropicModel
from ..models.generation_error_details import ErrorGenerationModel

class AnthropicClient:
    async_methods = ['fetch_completion']

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.logger = self.setup_logger()
        self.client = self.initialize_client(api_key)

    def setup_logger(self):
        logger = logging.getLogger(__name__)
        logger.setLevel(logging.DEBUG)
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        return logger

    def initialize_client(self, api_key: str):
        # Replace with actual initialization of the Anthropic client
        return None

    async def fetch_completion(self, anthropic_model: AnthropicModel, prompt: str, id: str) -> AsyncIterable[bytes]:
        try:
            self.logger.debug(f"Fetching streaming completion for model: {anthropic_model.id}")

            # Replace with actual API call to Anthropic
            stream = await self.client.get_completions(
                model=anthropic_model.id,
                prompt=prompt,
                temperature=0.0,
                stream=True
            )

            async def async_generator():
                full_content = ""
                async for chunk in stream:
                    content = chunk.get('content', '')
                    full_content += content

                    completion = Completion(
                        id=id,
                        choices=[Choice(
                            finish_reason=chunk.get('finish_reason', 'null'),
                            index=0,
                            message=Message(
                                content=full_content,
                                role="assistant"
                            )
                        )],
                        created=chunk.get('created', ''),
                        model=anthropic_model.id,
                        object=chunk.get('object', ''),
                        system_fingerprint=None,
                        usage=Usage(completion_tokens=0, prompt_tokens=0, total_tokens=0)
                    )

                    yield (SuccessGenerationModel(
                        id=id,
                        model=anthropic_model.id,
                        completion=completion
                    ).model_dump_json()).encode('utf-8')

            return async_generator()

        except Exception as e:
            self.logger.error(f"AnthropicClient::fetch_completion: Error with model {anthropic_model.id}: {str(e)}")

            async def error_generator(error: str) -> AsyncIterable[bytes]:
                yield (ErrorGenerationModel(
                    model=anthropic_model.id,
                    error=error
                ).model_dump_json()).encode('utf-8')

            return error_generator(str(e))

    async def get_available_models(self) -> list:
        """
        Fetches the list of available models from Anthropic.
        """
        try:
            response = await self.client.list_models()  # Replace with actual method
            models = [
                AnthropicModel.from_dict(model.model_dump())  # Use the factory method to create each model
                for model in response.data
            ]

            self.logger.debug(f"Retrieved {len(models)} models from Anthropic")
            return models
        except Exception as e:
            self.logger.error(f"Failed to fetch models from Anthropic: {str(e)}", exc_info=True)
            raise ValueError(f"Error fetching models from Anthropic: {str(e)}")
