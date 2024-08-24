import os
from llama_cpp import Llama
from .base_client import BaseClient
from ..models.stream_response import StreamResponse
import json
import time

class LLamaCppClient(BaseClient):
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



    def stream_response(self,model, prompt,prompt_id):
        output = self.generate(
            prompt,
            max_tokens=1000,
            temperature=0.9,
            top_p=0.95,
            stop=["Q:", "\n"],
            echo=False
        )
        if 'choices' in output and len(output['choices']) > 0 and output['choices'][0]['text']:
            generated_text = output['choices'][0]['text']
            for token in generated_text.split():
                response = StreamResponse(status="data", token=token,
                                                             message=generated_text)
                yield json.dumps(response)
                time.sleep(0.1)
            yield json.dumps(StreamResponse(status="end"))
        else:
            yield json.dumps(
                StreamResponse(status="error", message="Empty or invalid local model output", model=model))