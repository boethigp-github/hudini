import os
from dotenv import load_dotenv

# Load environment variables from .env.local
env_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '.env.local'))
if not os.path.exists(env_path):
    raise FileNotFoundError(f".env.local file not found at {env_path}. Please ensure the file exists.")
load_dotenv(env_path)

class Config:
    # Flask settings
    DEBUG = True  # Enable debug mode
    TESTING = False  # Disable testing mode

    # Swagger settings
    SWAGGER_URL = '/api/docs'  # URL for exposing Swagger UI (without trailing '/')
    API_URL = '/swagger.yaml'  # Path to Swagger YAML file

    # OpenAI API configuration
    OPENAI_API_KEY = os.getenv('API_KEY_OPEN_AI')
    if not OPENAI_API_KEY:
        raise ValueError("OpenAI API key not set. Please check your .env.local file.")

    # Model configuration
    MODEL_PATH = os.getenv('PROJECT_MODEL_PATH')
    if not MODEL_PATH:
        raise ValueError("Model path not set. Please check your .env.local file.")

    # SQLAlchemy settings
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')
    if not SQLALCHEMY_DATABASE_URI:
        raise ValueError("Database URL not set. Please check your .env.local file.")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

