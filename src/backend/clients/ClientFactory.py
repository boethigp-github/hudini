from .LocalClient import LocalClient
from .OpenAIClient import OpenAIClient

class ClientFactory:
    @staticmethod
    def get_client(client_type, **kwargs):
        if client_type == 'local':
            return LocalClient(kwargs.get('model_path'))
        elif client_type == 'openai':
            return OpenAIClient(kwargs.get('api_key'))
        else:
            raise ValueError(f"Unknown client type: {client_type}")
