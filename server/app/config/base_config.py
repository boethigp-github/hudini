import os
from dotenv import load_dotenv


class BaseConfig:
    # Load the .env.local file
    env_path = os.path.abspath(
        os.path.join(os.path.dirname(__file__), '..', '..', '..', 'infrastructure', 'environment', '.env.local'))
    if not os.path.exists(env_path):
        raise FileNotFoundError(f".env.local file not found at {env_path}. Please ensure the file exists.")

    load_dotenv(env_path)

    # Flask settings as class attributes
    FLASK_DEBUG = os.getenv('FLASK_DEBUG', 'False').lower() in ('true', '1', 't')
    FLASK_ENV = os.getenv('FLASK_ENV')
    APP_LOG_LEVEL = os.getenv('APP_LOG_LEVEL')
    APP_PROJECT_NAME = os.getenv('APP_PROJECT_NAME')
    TESTING = True  # Disable testing mode

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

    #CORS
    CORS_ORIGINS = os.getenv('CORS_ORINGIN','http://localhost:5173')  # Default for development

