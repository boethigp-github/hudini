import logging
from openai import AsyncOpenAI
from server.app.models.success_generation_model import SuccessGenerationModel
from server.app.models.error_generation_model import ErrorGenerationModel

class OpenAIClient:
    def __init__(self, api_key: str):
        self.client = AsyncOpenAI(api_key=api_key)
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
