from fastapi import APIRouter, HTTPException, Depends, Request
from typing import List
from server.app.config.settings import Settings
from server.app.clients.openai.openai_client import OpenAIClient
from server.app.clients.anthropic.anthropic_client import AnthropicClient
from server.app.clients.googleai.google_ai_client import GoogleAICLient
import logging
from server.app.models.models.models_get_response import ModelGetResponseModel  # Your provided path
import os

# Initialize the logger
logger = logging.getLogger("models_router")
settings = Settings()  # Initialize settings

# Initialize the router
router = APIRouter()


# Define the function to get cache from the request's application state
def get_cache(request: Request):
    return request.app.state.cache


def get_active_providers():
    """
    Retrieve the active providers from the environment variable APP_ACTIVE_PROVIDER.
    Returns a list of activated providers or an empty list if none are set.
    """
    active_providers = os.getenv("APP_ACTIVE_PROVIDER", "")
    if active_providers:
        return active_providers.split(",")
    return []


@router.get("/models", response_model=List[ModelGetResponseModel], tags=["models"])
async def get_models(cache=Depends(get_cache)):
    """
    Retrieves available models from the activated providers,
    merges them into a single list, and returns them as a JSON response.
    The results are cached for 300 seconds (5 minutes).
    """
    try:
        # Get the active providers from environment
        active_providers = get_active_providers()

        if not active_providers:
            logger.warning("No active providers found, returning empty model list.")
            cache.set("models_list", [], expire=300)  # Cache the empty result
            return []  # No active providers, return an empty list

        # Create a cache key that includes the active providers
        cache_key = f"models_list_{'_'.join(active_providers)}"

        # Check if the result is in the cache for the active providers
        cached_models = cache.get(cache_key)
        if cached_models is not None:
            logger.debug("Cache hit: Returning cached models list for active providers")
            return cached_models  # The response model handles the serialization

        all_models = []

        # Retrieve models from the active providers
        if "OPEN_AI" in active_providers:
            openai_models = OpenAIClient(api_key=settings.get("default").get("API_KEY_OPEN_AI")).get_available_models()
            all_models.extend(openai_models)
        if "ANTHROPIC" in active_providers:
            anthropic_models = AnthropicClient(api_key=settings.get("default").get("API_KEY_ANTHROPIC")).get_available_models()
            all_models.extend(anthropic_models)
        if "GOOGLE_AI" in active_providers:
            google_ai_models = GoogleAICLient(api_key=settings.get("default").get("API_KEY_GOOGLE_AI")).get_available_models()
            all_models.extend(google_ai_models)

        # Cache the models, even if it's an empty list, specific to the active providers
        cache.set(cache_key, all_models, expire=300)
        logger.debug("Cache miss: Retrieved and cached new models list for active providers")

        return all_models
    except Exception as e:
        logger.error(f"Error retrieving models: {str(e)}")
        raise HTTPException(status_code=500, detail=f"An error occurred while retrieving models: {str(e)}")
