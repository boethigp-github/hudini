import logging
from typing import AsyncGenerator
import google.generativeai as genai
from datetime import datetime
from server.app.models.generation.google_ai_model import GoogleAIModel
from server.app.models.generation.generation_request import GenerationRequest, ModelConfig
from server.app.models.generation.success_generation_model import SuccessGenerationModel, Completion, Choice, Message, \
    Usage


class GoogleAICLient:
    async_methods = ['fetch_completion']

    def __init__(self, api_key: str) -> None:
        self.api_key = api_key
        genai.configure(api_key=api_key)
        self.logger = self.setup_logger()
        self.logger.debug(f"GoogleAICLient initialized with API key: {api_key[:5]}...")

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

    async def generate(self, model_config: ModelConfig, request: GenerationRequest) -> AsyncGenerator[bytes, None]:
        model = genai.GenerativeModel(model_config.model)
        response = model.generate_content(request.prompt, stream=True)
        full_content = ''

        # Use synchronous iteration over the response, assuming it's a regular iterator
        for chunk in response:
            full_content += chunk.text
            success_model = SuccessGenerationModel(
                id=request.id,
                model=model_config.model,
                completion=Completion(
                    id=request.id,
                    choices=[Choice(
                        finish_reason="complete",
                        index=1,
                        message=Message(
                            content=full_content,
                            role="assistant"
                        )
                    )],
                    created=int(datetime.utcnow().timestamp()),
                    model=model_config.model,
                    object="model",
                    system_fingerprint=None,
                    usage=Usage(
                        completion_tokens=len(full_content.split()),  # Calculate tokens using accumulated content
                        prompt_tokens=len(request.prompt.split()),
                        total_tokens=len(full_content.split()) + len(request.prompt.split()),
                        ended=int(datetime.utcnow().timestamp())
                    )
                ),
                finish_reason="complete"
            )
            self.logger.debug(f"SuccessModel Google AI: {success_model.model_dump_json()}")
            yield success_model.model_dump_json().encode('utf-8') + b'\n'

    def get_available_models(self) -> list:
        try:
            # Fetch the list of models from the genai API
            models = genai.list_models()

            # Filter the models that support the desired generation methods
            available_models = []
            for model in models:
                if "generateContent" in model.supported_generation_methods:
                    available_models.append(
                        GoogleAIModel(
                            id=model.name,
                            model=model.name,
                            created=int(datetime.utcnow().timestamp()),
                            platform="google",
                            category='text_completion'
                        )
                    )

            self.logger.debug(f"Retrieved {len(available_models)} models from Google AI")
            return [model.model_dump() for model in available_models]

        except Exception as e:
            self.logger.error(f"GoogleAICLient::get_available_models: Failed to fetch models from Google AI: {str(e)}",
                              exc_info=True)
            raise ValueError(f"GoogleAICLient::get_available_models: Error fetching models from Google AI: {str(e)}")
