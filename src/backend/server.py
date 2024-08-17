# In server.py or the main script where create_app is called
import os
import sys
from app import create_app
from clients.ClientFactory import ClientFactory

if __name__ == "__main__":
    app = create_app()

    # Instantiate the OpenAI client after the environment is loaded
    openai_api_key = os.getenv('API_KEY_OPEN_AI')
    if not openai_api_key:
        raise ValueError("OpenAI API key is not set. Check your .env.local file.")

    openai_client = ClientFactory.get_client('openai', api_key=openai_api_key)

    app.run(host='0.0.0.0', port=5000, debug=True)
