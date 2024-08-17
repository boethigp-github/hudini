# app/services/openai_service.py
import os
from clients.ClientFactory import ClientFactory

def get_openai_client():
    openai_api_key = os.getenv('API_KEY_OPEN_AI')
    if not openai_api_key:
        raise ValueError("OpenAI API key is not set. Check your .env.local file.")

    return ClientFactory.get_client('openai', api_key=openai_api_key)
