import os
import logging
from .openai_client import OpenAIClient  # Correctly import OpenAIClient
from .local_client import LocalClient  # Ensure LocalClient is also correctly imported

logger = logging.getLogger(__name__)

class ClientFactory:
    @staticmethod
    def get_client(client_type, api_key=None, **kwargs):
        if client_type == 'openai':
            if not api_key:
                logger.error("API key must be provided to create the OpenAI client.")
                return None
            logger.info("Creating OpenAIClient with the provided API key.")
            return OpenAIClient(api_key)

        elif client_type == 'local':
            model_path = kwargs.get('model_path')
            logger.info(f"Attempting to create LocalClient with model path: {model_path}")
            if not model_path or not os.path.exists(model_path):
                logger.error(f"Invalid model path provided: {model_path}")
                return None
            try:
                client = LocalClient(model_path)
                logger.info(f"LocalClient created successfully with model path: {model_path}")
                return client
            except Exception as e:
                logger.exception(f"Failed to create LocalClient: {str(e)}")
                return None

        else:
            logger.error(f"Unsupported client type: {client_type}")
            return None
