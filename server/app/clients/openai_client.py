import logging
import openai
from openai import AsyncOpenAI
from server.app.models.success_generation_model import SuccessGenerationModel
from server.app.models.error_generation_model import ErrorGenerationModel
from server.app.models.openai_model import OpenAIModel  # Import the new Pydantic model

class OpenAIClient:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.client = AsyncOpenAI(api_key=api_key)  # For async operations
        openai.api_key = api_key  # For synchronous operations
        self.logger = self.setup_logger()

    def setup_logger(self):
        logger = logging.getLogger(__name__)
        logger.setLevel(logging.DEBUG)
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        return logger

    async def fetch_completion(self, model: str, prompt: str) -> str:
        try:
            completion = await self.client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.0
            )

            return SuccessGenerationModel(
                model=model,
                completion=completion.to_dict()
            ).model_dump_json()

        except Exception as e:
            self.logger.error(f"Error with model {model}: {str(e)}")
            return ErrorGenerationModel(
                model=model,
                error=str(e)
            ).model_dump_json()

    def get_available_models(self) -> list:
        """
        Fetches the list of available models from OpenAI using the synchronous OpenAI client.

        Returns:
            list: A list of OpenAIModel instances representing the models available in the OpenAI API.
        """
        try:
            response = openai.models.list()  # Synchronous call to fetch models
            models = [
                OpenAIModel.from_dict(model.to_dict()).model_dump()  # Use the factory method to create each model
                for model in response.data
            ]

            self.logger.debug(f"Retrieved {len(models)} models from OpenAI")
            return models
        except Exception as e:
            self.logger.error(f"Failed to fetch models from OpenAI: {str(e)}", exc_info=True)
            raise ValueError(f"Error fetching models from OpenAI: {str(e)}")
