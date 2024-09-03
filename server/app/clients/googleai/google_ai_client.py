import logging
from typing import AsyncGenerator
import google.generativeai as genai
from datetime import datetime
import os
import json
from server.app.models.generation.google_ai_model import GoogleAIModel
# Assuming you have these model imports
from server.app.models.generation.generation_request import GenerationRequest, ModelConfig
from server.app.models.generation.success_generation_model import SuccessGenerationModel, Completion, Choice, Message, Usage

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
        try:
            models = [
                GoogleAIModel(id="gemini-1.0-pro",
                              model="gemini-1.0-pro",
                              created=int(datetime.utcnow().timestamp()),
                              platform="google",
                              category='text_completion'
                              ),
                GoogleAIModel(id="gemini-1.5-pro",
                              model="gemini-1.5-pro",
                              created=int(datetime.utcnow().timestamp()),
                              platform="google",
                              category='text_completion'
                              ),
                GoogleAIModel(id="gemini-1.5-pro-exp-0801",
                              model="gemini-1.5-pro-exp-0801",
                              created=int(datetime.utcnow().timestamp()),
                              platform="google",
                              category='text_completion'
                              ),
                GoogleAIModel(id="gemini-1.5-pro-exp-0827",
                              model="gemini-1.5-pro-exp-0827",
                              created=int(datetime.utcnow().timestamp()),
                              platform="google",
                              category='text_completion'
                              ),
                GoogleAIModel(id="gemini-1.5-flash",
                              model="gemini-1.5-flash",
                              created=int(datetime.utcnow().timestamp()),
                              platform="google",
                              category='text_completion'
                              ),
                GoogleAIModel(id="gemini-1.5-flash-exp-0827",
                              model="gemini-1.5-flash-exp-0827",
                              created=int(datetime.utcnow().timestamp()),
                              platform="google",
                              category='text_completion'
                              ),
                GoogleAIModel(id="gemma-2-2b-it",
                              model="gemma-2-2b-it",
                              created=int(datetime.utcnow().timestamp()),
                              platform="google",
                              category='text_completion'
                              ),
                GoogleAIModel(id="gemma-2-9b-it",
                              model="gemma-2-9b-it",
                              created=int(datetime.utcnow().timestamp()),
                              platform="google",
                              category='text_completion'
                              ),
                GoogleAIModel(id="gemma-2-27b-it",
                              model="gemma-2-27b-it",
                              created=int(datetime.utcnow().timestamp()),
                              platform="google",
                              category='text_completion'
                              )
            ]

            self.logger.debug(f"Retrieved {len(models)} models from Google AI")
            return [model.model_dump() for model in models]
        except Exception as e:
            self.logger.error(f"GoogleAICLient::get_available_models: Failed to fetch models from Google AI: {str(e)}",
                              exc_info=True)
            raise ValueError(f"GoogleAICLient::get_available_models: Error fetching models from Google AI: {str(e)}")
