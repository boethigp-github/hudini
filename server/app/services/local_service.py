import os
import logging
from server.app.clients.client_factory import ClientFactory

logger = logging.getLogger(__name__)

local_client = None

def initialize_local_client():
    global local_client
    logger.info("Attempting to initialize local client")

    try:
        model_path = os.getenv('PROJECT_MODEL_PATH')
        if not model_path or not os.path.isdir(model_path):
            logger.error(f"Invalid or missing PROJECT_MODEL_PATH: {model_path}")
            return None

        logger.info(f"PROJECT_MODEL_PATH is set to: {model_path}")
        local_client = ClientFactory.get_client('local', model_path=model_path)

        if local_client is None:
            logger.error("ClientFactory.get_client returned None")
            return None

        logger.info("Local client initialized successfully")
        return local_client

    except Exception as e:
        logger.exception(f"Exception occurred while initializing local client: {str(e)}")
        return None

def get_local_client():
    global local_client
    if local_client is None:
        logger.info("Local client is None, attempting to reinitialize.")
        local_client = initialize_local_client()
    return local_client

# Attempt to initialize the client at import time
if initialize_local_client() is None:
    logger.warning("Failed to initialize local client at import. Will attempt to initialize later.")
