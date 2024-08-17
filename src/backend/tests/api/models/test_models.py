import requests
import os
from dotenv import load_dotenv

# Get the current file's directory
current_dir = os.path.dirname(os.path.abspath(__file__))

# Construct the path to .env.local
env_path = os.path.join(current_dir, '..', '..', '.env.local')

# Load environment variables from .env.local
load_dotenv(env_path)

BASE_URL = os.getenv('SERVER_URL', 'http://localhost:5000')

def test_get_models():
    response = requests.get(f"{BASE_URL}/get_models")
    assert response.status_code == 200
    data = response.json()
    assert 'local_models' in data
    assert 'openai_models' in data
    assert isinstance(data['local_models'], list)
    assert isinstance(data['openai_models'], list)
