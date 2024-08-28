import sys
import os
import uvicorn
import logging.config  # Make sure to import logging.config
from app.factory.fast_api_app_factory import FastAPIAppFactory
from app.config.settings import Settings  # Adjust import according to your project structure

# Ensure the Python path is set correctly
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Initialize the settings object
settings = Settings()

# Set up logging using the loaded configuration
logging_config = settings.get('default__LOGGING_CONFIG')
if logging_config:
    logging.config.dictConfig(logging_config)

# Create the FastAPI app
app_factory = FastAPIAppFactory()
app = app_factory.create_app(settings)

# Use the logger from the FastAPIAppFactory instance
logger = app_factory.logger

if __name__ == "__main__":
    debug = settings.get('default__DEBUG')
    logger.debug(f'DEBUG: {debug}')
    logger.debug(f'ENV: {settings.get("default__ENV")}')

    # Start the FastAPI app with Uvicorn using the APP_PORT from the settings
    uvicorn.run(
        "server.run:app",  # Reference to the app variable
        host="0.0.0.0",
        port=settings.get('default__APP_PORT'),  # Use the APP_PORT from the settings
        reload=debug,
        log_level="debug" if debug else "info"
    )
