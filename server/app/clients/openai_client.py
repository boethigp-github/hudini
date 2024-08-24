import logging
from openai import AsyncOpenAI
from openai import OpenAI
from server.app.models.success_generation_model import SuccessGenerationModel
from server.app.models.error_generation_model import ErrorGenerationModel

class OpenAIClient:
    def __init__(self, api_key: str):
        self.client = AsyncOpenAI(api_key=api_key)
        self.sync_client = OpenAI(api_key=api_key)
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

            # Use the SuccessGenerationModel to validate and serialize the response
            return SuccessGenerationModel(
                model=model,
                completion=completion.to_dict()
            ).model_dump_json()

        except Exception as e:
            self.logger.error(f"Error with model {model}: {str(e)}")
            # Use the ErrorGenerationModel to validate and serialize the error response
            return ErrorGenerationModel(
                model=model,
                error=str(e)
            ).model_dump_json()

    def get_available_models(self):
        """
        Get a list of available models from OpenAI, with caching using cachetools.

        Returns:
            list: A list of model IDs available in the OpenAI account.
        """
        # if 'models' in self.cache:
        #     self.logger.debug(f"Cache Hit on get_available_models()", exc_info=True)
        #     return self.cache['models']

        try:
            # List all models available in the account
            response = self.sync_client.models.list()
            models = [model.id for model in response]

            # Cache the result
            # self.cache['models'] = models
            # self.logger.debug(f"Cache  {len(models)} Models")
            return models
        except Exception as e:
            # Log the detailed error before raising an exception
            self.logger.error(f"Failed to fetch models from OpenAI: {str(e)}", exc_info=True)
            raise ValueError(f"Error fetching models from OpenAI: {str(e)}")