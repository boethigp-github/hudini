import logging
from datetime import datetime

import openai
from openai import AsyncOpenAI
from server.app.models.generation.success_generation_model import SuccessGenerationModel, Completion, Choice, Message, \
    Usage
from server.app.models.generation_error_details import ErrorGenerationModel
from server.app.models.generation.openai_model import OpenaiModel
from typing import Optional


class OpenAIClient:
    async_methods = ['fetch_completion']

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.client = AsyncOpenAI(api_key=api_key)  # For async operations
        openai.api_key = api_key  # For synchronous operations
        self.logger = self.setup_logger()

        self.logger.debug(f"OpenAIClient IN_PROGRESS with API key: {api_key[:5]}...")

    def setup_logger(self):
        logger = logging.getLogger(__name__)
        logger.setLevel(logging.DEBUG)
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        return logger

    async def fetch_completion(self, openai_model: OpenaiModel, prompt: str, id: str,
                               presence_penalty: Optional[float] = 0.0):
        try:
            self.logger.debug(
                f"Fetching streaming completion for model: {openai_model.id} with presence_penalty: {presence_penalty}")
            stream = await self.client.chat.completions.create(
                model=openai_model.id,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.0,
                stream=True,
                presence_penalty=presence_penalty  # Setze den presence_penalty hier
            )

            async def async_generator():
                full_content = ""
                async for chunk in stream:
                    self.logger.debug(
                        f"OpenAIClient::fetch_completion_stream chunk: {chunk}")
                    if chunk.choices[0].delta.content is not None:
                        content = chunk.choices[0].delta.content
                        full_content += content

                        # Construct a Completion object for each chunk
                        completion = Completion(
                            id=chunk.id,
                            choices=[Choice(
                                finish_reason=chunk.choices[0].finish_reason or "null",
                                index=chunk.choices[0].index,
                                message=Message(
                                    content=full_content,
                                    role=chunk.choices[0].delta.role or "assistant"
                                )
                            )],
                            created=chunk.created,
                            model=openai_model.id,
                            object=chunk.object,
                            # Assuming these are not available in streaming mode
                            system_fingerprint=None,
                            usage=Usage(
                                completion_tokens=len(full_content.split()),
                                # Calculate tokens using accumulated content
                                prompt_tokens=len(prompt.split()),
                                total_tokens=len(full_content.split()) + len(prompt.split()),
                                ended=int(datetime.utcnow().timestamp())
                            )
                        )

                        yield (SuccessGenerationModel(
                            id=id,
                            model=openai_model.id,
                            completion=completion
                        ).model_dump_json()).encode('utf-8')

            return async_generator()

        except Exception as e:
            self.logger.error(f"OpenAIClient::fetch_completion_stream: Error with model {openai_model.id}: {str(e)}")

            async def error_generator(error: str):
                yield (ErrorGenerationModel(
                    model=openai_model.id,
                    error=error
                ).model_dump_json()).encode('utf-8')

            return error_generator(str(e))

    def get_available_models(self) -> list:
        """
        Fetches the list of available models from OpenAI using the synchronous OpenAI client.

        Returns:
            list: A list of OpenaiModel instances representing the models available in the OpenAI API.
        """
        try:
            response = openai.models.list()  # Synchronous call to fetch models
            models = [
                OpenaiModel.from_dict(model.model_dump()).model_dump()  # Use the factory method to create each model
                for model in response.data
            ]

            self.logger.debug(f"Retrieved {len(models)} models from OpenAI")
            return models
        except Exception as e:
            self.logger.error(f"Failed to fetch models from OpenAI: {str(e)}", exc_info=True)
            raise ValueError(f"Error fetching models from OpenAI: {str(e)}")
