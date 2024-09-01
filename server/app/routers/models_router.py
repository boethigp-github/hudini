from fastapi import APIRouter, HTTPException, Depends, Request
from fastapi.responses import JSONResponse
from ..config.settings import Settings
from ..clients.openai_client import OpenAIClient
from ..clients.anthropic_client import AnthropicClient
import logging
from typing import List
from ..models.models.models_get_response import ModelGetResponseModel
# Initialize the logger
logger = logging.getLogger("models_router")

# Initialize the settings
settings = Settings()

# Initialize the routers
router = APIRouter()
logging.basicConfig(level=logging.WARNING)
# Inject the cache dependency from the app state
def get_cache(request: Request):
    return request.app.state.cache

@router.get("/models", response_model=List[ModelGetResponseModel], tags=["models"])
async def get_models(cache=Depends(get_cache)):
    """
    Handles the /models route.

    This method retrieves available models from OpenAI and Anthropic,
    merges them into a single list, and returns them as a JSON response.

    The results are cached for 300 seconds (5 minutes).

    Returns:
        List[ModelGetResponseModel]: A list of all available models.
    """
    try:
        # Check if the result is in the cache
        cached_models = cache.get("models_list")
        if cached_models:
            logger.debug("Cache hit: Returning cached models list")
            return cached_models  # The response model handles the serialization

        # Retrieve models from OpenAI and Anthropic
        openai_models = OpenAIClient(api_key=settings.get("default").get("API_KEY_OPEN_AI")).get_available_models()
        #anthropic_models = AnthropicClient(api_key=settings.get("default").get("API_KEY_ANTHROPIC")).get_available_models()
        anthropic_models = []

        # Merge all models into a single list
        all_models = openai_models + anthropic_models

        # Store the result in the cache
        cache.set("models_list", all_models, expire=300)

        logger.debug("Cache miss: Retrieved and cached new models list")

        # Return the complete list of models
        return all_models
    except Exception as e:
        logger.error(f"Error retrieving models: {str(e)}")
        raise HTTPException(status_code=500, detail=f"An error occurred while retrieving models {str(e)}")
