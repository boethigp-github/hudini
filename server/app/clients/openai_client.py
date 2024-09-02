import logging
import openai
from openai import AsyncOpenAI
from server.app.models.generation.success_generation_model import SuccessGenerationModel, Completion, Choice, Message, \
    Usage
from ..models.generation_error_details import ErrorGenerationModel
from ..models.openai_model import OpenaiModel
from typing import Optional, AsyncGenerator, List
import asyncio
import json


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
                               presence_penalty: Optional[float] = 0.0) -> AsyncGenerator[bytes, None]:
        try:
            self.logger.debug(
                f"Fetching streaming completion for model: {openai_model.id} with presence_penalty: {presence_penalty}")

            async def async_generator():
                full_content = ""
                async for chunk in await self.client.chat.completions.create(
                        model=openai_model.id,
                        messages=[
                            {"role": "system", "content": "You are a helpful assistant."},
                            {"role": "user", "content": prompt}
                        ],
                        temperature=0.0,
                        stream=True,
                        presence_penalty=presence_penalty
                ):
                    if chunk.choices[0].delta.content is not None:
                        content = chunk.choices[0].delta.content
                        full_content += content

                        completion = Completion(
                            choices=[Choice(
                                message=Message(
                                    content=full_content,
                                    role=chunk.choices[0].delta.role or "assistant"
                                )
                            )],
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

    async def generate(self, models: List[OpenaiModel], prompt: str, id: str) -> AsyncGenerator[bytes, None]:
        tasks = []
        for model in models:
            async_task = self.fetch_completion(model, prompt, id)
            task = asyncio.create_task(async_task)
            tasks.append(task)

        for completed_task in asyncio.as_completed(tasks):
            async_gen = await completed_task
            async for result in async_gen:
                if isinstance(result, bytes):
                    result = result.decode('utf-8')
                yield result.encode('utf-8') + b'\n'

    def get_available_models(self) -> list:
        try:
            response = openai.models.list()
            models = [
                OpenaiModel.from_dict(model.model_dump()).model_dump()
                for model in response.data
            ]
            self.logger.debug(f"Retrieved {len(models)} models from OpenAI")
            return models
        except Exception as e:
            self.logger.error(f"Failed to fetch models from OpenAI: {str(e)}", exc_info=True)
            raise ValueError(f"Error fetching models from OpenAI: {str(e)}")
