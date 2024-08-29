import sys
import os
from server.app.factory.fast_api_app_factory import FastAPIAppFactory
from server.app.utils.hudini_logger import hudini_logger  # Import the global hudini_logger
from server.app.config.settings import Settings

# Ensure the root of the project is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))

# Initialize settings
settings = Settings()

# Initialize FastAPIAppFactory with the global logger
app_factory = FastAPIAppFactory(settings)

# Create the FastAPI app
app = app_factory.create_app()

if __name__ == "__main__":
    import uvicorn
    port = int(settings.get('APP_PORT', 80))
    hudini_logger.info(f"Starting Uvicorn server on port {port}")
    uvicorn.run(app, host="0.0.0.0", port=port, reload=False)
