import logging
import json
import openai
from openai import AsyncOpenAI
from server.app.models.success_generation_model import SuccessGenerationModel, Completion, Choice, Message, Usage
from server.app.models.generation_error_details import ErrorGenerationModel
from server.app.models.openai_model import OpenaiModel

class OpenAIClient:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.client = AsyncOpenAI(api_key=api_key)  # For async operations
        openai.api_key = api_key  # For synchronous operations
        self.logger = self.setup_logger()

        self.logger.debug(f"OpenAIClient initialized with API key: {api_key[:5]}...")

    def setup_logger(self):
        logger = logging.getLogger(__name__)
        logger.setLevel(logging.DEBUG)
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        return logger




    async def fetch_completion(self, model: OpenaiModel, prompt: str, prompt_id: str):
        try:
            self.logger.debug(f"Fetching streaming completion for model: {model.id}")
            stream = await self.client.chat.completions.create(
                model=model.id,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.0,
                stream=True
            )

            async def async_generator():
                full_content = ""
                async for chunk in stream:
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
                            model=chunk.model,
                            object=chunk.object,
                            # Assuming these are not available in streaming mode
                            system_fingerprint=None,
                            usage=Usage(completion_tokens=0, prompt_tokens=0, total_tokens=0)
                        )

                        yield (SuccessGenerationModel(
                            prompt_id=prompt_id,
                            model=model.id,
                            completion=completion
                        ).model_dump_json()).encode('utf-8')

            return async_generator()

        except Exception as e:
            self.logger.error(f"OpenAIClient::fetch_completion_stream: Error with model {model.id}: {str(e)}")

            async def error_generator():
                yield (ErrorGenerationModel(
                    model=model.id,
                    error=str(e)
                ).model_dump_json() + '\n').encode('utf-8')

            return error_generator()

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