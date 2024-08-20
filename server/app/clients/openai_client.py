from .base_client import BaseClient
import openai  # Correctly import the openai package


class OpenAIClient(BaseClient):
    def __init__(self, api_key):
        if not api_key:
            raise ValueError("OpenAI API key is not set")
        openai.api_key = api_key  # Set the API key for the openai package

    def generate(self, prompt: str, **kwargs):
        """
        Generate a completion for a given prompt using the OpenAI API.

        Args:
            prompt (str): The prompt to send to the OpenAI model.
            **kwargs: Additional parameters like model, max_tokens, etc.

        Returns:
            str: The content generated by the model.
        """
        response = openai.ChatCompletion.create(
            model=kwargs.get('model', 'gpt-3.5-turbo'),
            messages=[{"role": "user", "content": prompt}],
            max_tokens=kwargs.get('max_tokens', 1000),
            temperature=kwargs.get('temperature', 0.7),
        )
        return response.choices[0].message['content']

    def get_available_models(self):
        """
        Get a list of available models from OpenAI.

        Returns:
            list: A list of model IDs available in the OpenAI account.
        """
        try:
            # List all models available in the account
            response = openai.Model.list()
            models = [model.id for model in response['data']]
            return models
        except Exception as e:
            raise ValueError(f"Error fetching models from OpenAI: {str(e)}")
