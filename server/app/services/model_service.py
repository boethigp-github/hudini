# app/services/model_service.py
import openai
import os

def get_local_models():
    model_dir = os.getenv('PROJECT_MODEL_PATH')
    if not model_dir:
        raise ValueError("PROJECT_MODEL_PATH is not set in the environment variables.")
    if not os.path.isdir(model_dir):
        raise ValueError(f"The directory specified in PROJECT_MODEL_PATH does not exist: {model_dir}")
    models = [f for f in os.listdir(model_dir) if os.path.isfile(os.path.join(model_dir, f))]
    return models



def get_openai_models():
    api_key = os.getenv('API_KEY_OPEN_AI')
    if not api_key:
        raise ValueError("OpenAI API key is not set in the environment variables.")

    client = openai.OpenAI(api_key=api_key)

    try:
        # List all models available in the account
        response = client.models.list()
        models = [model.id for model in response.data]
        return models
    except Exception as e:
        raise ValueError(f"Error fetching models from OpenAI: {str(e)}")
