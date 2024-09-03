import logging
from typing import AsyncGenerator, List
import anthropic
from server.app.models.generation.success_generation_model import SuccessGenerationModel, Completion, Choice, Message, Usage
from server.app.models.generation.generation_request import GenerationRequest, ModelConfig
from server.app.models.generation.anthropic_model import AnthropicModel
from datetime import datetime
class AnthropicClient:
    async_methods = ['fetch_completion']

    def __init__(self, api_key: str) -> None:
        self.api_key = api_key
        self.client = anthropic.Anthropic(api_key=api_key)
        self.logger = self.setup_logger()
        self.logger.debug(f"AnthropicClient initialized with API key: {api_key[:5]}...")

    def setup_logger(self) -> logging.Logger:
        logger = logging.getLogger(__name__)
        logger.setLevel(logging.DEBUG)
        if not logger.hasHandlers():
            handler = logging.StreamHandler()
            handler.setLevel(logging.DEBUG)
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        return logger

    async def generate(self, models: List[ModelConfig], request: GenerationRequest) -> AsyncGenerator[bytes, None]:
        for model_config in models:
            async for result in self._stream_model_response(model_config, request):
                yield result

    async def _stream_model_response(self, model_config: ModelConfig, request: GenerationRequest) -> AsyncGenerator[bytes, None]:
        with self.client.messages.stream(
                max_tokens=model_config.max_tokens,
                messages=[{"role": "user", "content": request.prompt}],
                model=model_config.model,
        ) as stream:
            full_content = ""
            for text in stream.text_stream:
                full_content +=text
                completion = Completion(
                    id=request.id,
                    choices=[Choice(
                        finish_reason="null",
                        index=1,
                        message=Message(
                            content=full_content,
                            role="assistant"
                        )
                    )],
                    created=11111,
                    model=model_config.model,
                    object="model",
                    system_fingerprint=None,
                    usage=Usage(completion_tokens=0, prompt_tokens=0, total_tokens=0)
                )

                success_model = SuccessGenerationModel(
                    id=request.id,
                    model=model_config.model,
                    completion=completion,
                    finish_reason="incomplete"  # Adjust as needed
                )


                yield success_model.model_dump_json().encode('utf-8') + b'\n'

    def get_available_models(self) -> list:
        try:
            models = [
                AnthropicModel(id="claude-3-5-sonnet-20240620",
                               model="claude-3-5-sonnet-20240620",
                               created=int(datetime.utcnow().timestamp()),
                               platform="anthropic",
                               category='text_completion'
                               ),
                AnthropicModel(id="claude-3-opus-20240229",
                               model="claude-3-opus-20240229",
                               created=int(datetime.utcnow().timestamp()),
                               platform="anthropic",
                               category='embedding'),
                AnthropicModel(id="claude-3-sonnet-20240229",
                               model="claude-3-sonnet-20240229",
                               created=int(datetime.utcnow().timestamp()),
                               platform="anthropic",
                               category='text_completion'),
                AnthropicModel(id="claude-3-haiku-20240307",
                               model="claude-3-haiku-20240307",
                               created=int(datetime.utcnow().timestamp()),
                               platform="anthropic",
                               category='text_completion'
                               )
            ]

            self.logger.debug(f"Retrieved {len(models)} models from Anthropic")
            return [model.model_dump() for model in models]
        except Exception as e:
            self.logger.error(f"AnthropicClient::get_available_models: Failed to fetch models from Anthropic: {str(e)}", exc_info=True)
            raise ValueError(f"AnthropicClient::get_available_models: Error fetching models from Anthropic: {str(e)}")
