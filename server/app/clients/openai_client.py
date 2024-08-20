from openai import OpenAI
from .base_client import BaseClient

class OpenAIClient(BaseClient):
    def __init__(self, api_key):
        if not api_key:
            raise ValueError("OpenAI API key is not set")
        self.client = OpenAI(api_key=api_key)

    def generate(self, prompt: str, **kwargs):
        response = self.client.chat.completions.create(
            model=kwargs.get('model', 'gpt-3.5-turbo'),
            messages=[{"role": "user", "content": prompt}],
            max_tokens=kwargs.get('max_tokens', 1000),
            temperature=kwargs.get('temperature', 0.7),
        )
        return response.choices[0].message.content

    def get_available_models(self):
        return ['gpt-4', 'gpt-4-0314', 'gpt-3.5-turbo']
