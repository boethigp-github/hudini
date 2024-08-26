import logging
import openai
from openai import AsyncOpenAI
from server.app.models.success_generation_model import SuccessGenerationModel
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

    async def fetch_completion(self, model: OpenaiModel, prompt: str, prompt_id: str) -> str:
        try:
            self.logger.debug(f"Fetching completion for model: {model.id}")
            completion = await self.client.chat.completions.create(
                model=model.id,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.0
            )

            return SuccessGenerationModel(
                prompt_id=prompt_id,
                model=model.id,
                completion=completion.to_dict()
            ).model_dump_json()

        except Exception as e:
            self.logger.error(f"OpenAIClient::fetch_completion: Error with model {model.id}: {str(e)}")
            return ErrorGenerationModel(
                model=model.id,
                error=str(e)
            ).model_dump_json()

    def get_available_models(self) -> list:
        """
        Fetches the list of available models from OpenAI using the synchronous OpenAI client.

        Returns:
            list: A list of OpenaiModel instances representing the models available in the OpenAI API.
        """
        try:
            response = openai.models.list()  # Synchronous call to fetch models
            models = [
                OpenaiModel.from_dict(model.to_dict()).model_dump()  # Use the factory method to create each model
                for model in response.data
            ]

            self.logger.debug(f"Retrieved {len(models)} models from OpenAI")
            return models
        except Exception as e:
            self.logger.error(f"Failed to fetch models from OpenAI: {str(e)}", exc_info=True)
            raise ValueError(f"Error fetching models from OpenAI: {str(e)}")