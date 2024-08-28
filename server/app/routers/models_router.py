from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse, Response
from ..config.settings import Settings
from ..clients.openai_client import OpenAIClient
from ..clients.anthropic_client import AnthropicClient
import logging

# Initialize the logger
logger = logging.getLogger("models_router")

# Initialize the settings
settings = Settings()

# Initialize the routers
router = APIRouter()

@router.get("/models",  tags=["models"])
async def get_models():
    """
    Handles the /models route.

    This method retrieves available models from OpenAI and Anthropic,
    merges them into a single list, and returns them as a JSON response.

    Returns:
        JSONResponse: A JSON response containing a list of all available models.
    """
    try:
        # Retrieve models from OpenAI and Anthropic
        openai_models = OpenAIClient(api_key=settings.get("default").get("API_KEY_OPEN_AI")).get_available_models()
        anthropic_models = AnthropicClient(api_key=settings.get("default").get("API_KEY_ANTHROPIC")).get_available_models()

        # Merge all models into a single list
        all_models = openai_models + anthropic_models

        # # Log the retrieved models for debugging purposes
        # logger.debug(f"Retrieved OpenAI models: {openai_models}")
        # logger.debug(f"Retrieved Anthropic models: {anthropic_models}")
        # logger.debug(f"Total models retrieved: {len(all_models)}")

        # Return the complete list of models as a JSON response
        return JSONResponse(content=all_models)
    except Exception as e:
        logger.error(f"Error retrieving models: {str(e)}")
        raise HTTPException(status_code=500, detail=f"An error occurred while retrieving models {str(e)}")

@router.get("/favicon.ico",  tags=["models"])
async def get_favicon():
    """
    Handles the /favicon.ico route.

    This method returns a 204 No Content response for the favicon.ico request.

    Returns:
        Response: An empty response with a 204 status code.
    """
    return Response(status_code=204)
