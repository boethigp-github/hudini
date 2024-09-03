import logging
from typing import AsyncGenerator
import google.generativeai as genai
from server.app.models.generation.generation_request import GenerationRequest, ModelConfig
from datetime import datetime
from server.app.models.generation.success_generation_model import SuccessGenerationModel, Completion, Choice, Message, \
    Usage
import os
import json

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
        # Configure the model
        generation_config = {
            "temperature": model_config.temperature,
            "top_p": 0.95,
            "top_k": 64,
            "max_output_tokens": 8192,
            "response_mime_type": "text/plain",
            # Add any additional safety settings as needed
        }

        model = genai.GenerativeModel(
            model_name=model_config.model,
            generation_config=generation_config,
        )

        chat_session = model.start_chat(history=[])

        try:
            response = chat_session.send_message(request.prompt)
            completion = SuccessGenerationModel(
                id=request.id,
                model=model_config.model,
                completion=Completion(
                    id=request.id,
                    choices=[Choice(
                        finish_reason="complete",
                        index=1,
                        message=Message(
                            content=response.text,
                            role="assistant"
                        )
                    )],
                    created=int(datetime.utcnow().timestamp()),
                    model=model_config.model,
                    object="model",
                    system_fingerprint=None,
                    usage=Usage(completion_tokens=len(response.text.split()), prompt_tokens=len(request.prompt.split()),
                                total_tokens=len(response.text.split()) + len(request.prompt.split()))
                ),
                finish_reason="complete"
            )
            self.logger.debug(f"SuccessModel Google AI: {completion.model_dump_json()}")
            yield completion.model_dump_json().encode('utf-8') + b'\n'

        except genai.types.generation_types.StopCandidateException as e:
            self.logger.error(f"Generation stopped due to safety settings: {e}")
            yield json.dumps({"error": "Generation stopped due to safety concerns.", "details": str(e)}).encode(
                'utf-8') + b'\n'

    def get_available_models(self) -> list:
        # Implement model retrieval specific to Google AI
        pass
