from fastapi import APIRouter, HTTPException, Depends, Request
from typing import List
from ..config.settings import Settings
from ..clients.openai_client import OpenAIClient
from ..clients.anthropic_client import AnthropicClient
import logging
from ..models.models.models_get_response import ModelGetResponseModel  # Your provided path

# Initialize the logger
logger = logging.getLogger("models_router")
settings = Settings()  # Initialize settings

# Initialize the router
router = APIRouter()


# Define the function to get cache from the request's application state
def get_cache(request: Request):
    return request.app.state.cache


@router.get("/models", response_model=List[ModelGetResponseModel], tags=["models"])
async def get_models(cache=Depends(get_cache)):
    """
    Retrieves available models from OpenAI and Anthropic,
    merges them into a single list, and returns them as a JSON response.
    The results are cached for 300 seconds (5 minutes).
    """
    try:
        # # Check if the result is in the cache
        # cached_models = cache.get("models_list")
        # if cached_models:
        #     logger.debug("Cache hit: Returning cached models list")
        #     return cached_models

        # Retrieve models from OpenAI and potentially other sources
        openai_models = OpenAIClient(api_key=settings.get("default").get("API_KEY_OPEN_AI")).get_available_models()
        #openai_models = []
        anthropic_models = []
        #anthropic_models = AnthropicClient(api_key=settings.get("default").get("API_KEY_ANTHROPIC")).get_available_models()

        # Merge and cache the models
        all_models = openai_models + anthropic_models
        cache.set("models_list", all_models, expire=300)
        logger.debug("Cache miss: Retrieved and cached new models list")

        return all_models
    except Exception as e:
        logger.error(f"Error retrieving models: {str(e)}")
        raise HTTPException(status_code=500, detail=f"An error occurred while retrieving models: {str(e)}")
