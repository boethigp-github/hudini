import os
from llama_cpp import Llama
from .base_client import BaseClient

class LocalClient(BaseClient):
    def __init__(self, model_path):
        self.model_path = model_path
        self.llm = None

    def load_model(self, model_name):
        full_path = os.path.join(self.model_path, model_name)
        self.llm = Llama(model_path=str(full_path))

    def generate(self, prompt: str, **kwargs):
        if not self.llm:
            raise ValueError("Model not loaded. Call load_model first.")
        return self.llm(prompt, **kwargs)

    def get_available_models(self):
        return [f for f in os.listdir(self.model_path) if f.endswith('.gguf')]


