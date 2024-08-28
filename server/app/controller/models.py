from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import JSONResponse
import logging
from ..config.settings import Settings
from ..clients.llama_cpp_client import LLamaCppClient
from ..clients.openai_client import OpenAIClient
from ..clients.anthropic_client import AnthropicClient


class ModelsController:
    """
    A controller class responsible for handling routes related to models.

    This class sets up the necessary routes to retrieve models from local storage and external services (OpenAI, Anthropic),
    and handles requests for the favicon.
    """

    def __init__(self, app_logger):
        """
        Initializes the ModelsController instance.

        This method creates a FastAPI APIRouter for the models routes and registers the necessary routes.
        """
        self.router = APIRouter()
        self.logger = app_logger  # Use the logger passed from FastAPIAppFactory

        # Initialize the Settings instance
        self.settings = Settings()

        self.register_routes()

    def register_routes(self):
        """
        Registers routes to the FastAPI router.

        This method maps the /models and /favicon.ico routes to their respective handler methods.
        """
        self.router.add_api_route("/models", self.models, methods=["GET"])
        self.router.add_api_route("/favicon.ico", self.favicon)

    async def models(self):
        """
        Handles the /models route.

        This method retrieves available models from local storage, OpenAI, and Anthropic,
        merges them into a single list, and returns them as a JSON response.

        Returns:
            JSONResponse: A JSON response containing a list of all available models.
        """
        try:
            # Retrieve models from local storage (LLama.cpp), OpenAI, and Anthropic
            models_path = self.settings.project_model_path
            # llama_cpp_models = LLamaCppClient(models_path).get_available_models()
            openai_models = OpenAIClient(api_key=self.settings.API_KEY_OPEN_AI).get_available_models()
            anthropic_models = AnthropicClient(api_key=self.settings.api_key_anthropic).get_available_models()

            # Merge all models into a single list
            all_models = openai_models + anthropic_models

            # Log the retrieved models for debugging purposes
            # self.logger.debug(f"Retrieved LLama.cpp models: {llama_cpp_models}")
            self.logger.debug(f"Retrieved OpenAI models: {openai_models}")
            self.logger.debug(f"Retrieved Anthropic models: {anthropic_models}")
            self.logger.debug(f"Total models retrieved: {len(all_models)}")

            # Return the complete list of models as a JSON response
            return JSONResponse(content=all_models)
        except Exception as e:
            self.logger.error(f"Error retrieving models: {str(e)}")
            raise HTTPException(status_code=500, detail="An error occurred while retrieving models")

    async def favicon(self):
        """
        Handles the /favicon.ico route.

        This method returns a 204 No Content response for the favicon.ico request.

        Returns:
            Response: An empty response with a 204 status code.
        """
        return JSONResponse(status_code=204)
