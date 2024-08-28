from fastapi import APIRouter, HTTPException, Response
from fastapi.responses import FileResponse, RedirectResponse
import logging
from ..utils.swagger_loader import SwaggerLoader


class SwaggerUiController:
    """
    A controller class responsible for handling routes related to the Swagger UI and YAML file.
    """

    def __init__(self, app_logger):
        """
        Initializes the SwaggerUiController instance.

        This method creates a FastAPI APIRouter for serving the swagger.yaml file and the Swagger UI.
        """
        self.router = APIRouter()
        self.logger = app_logger  # Use the logger passed from FastAPIAppFactory
        self.register_routes()

    def register_routes(self):
        """
        Registers routes to the FastAPI router.
        """
        # Serve swagger.yaml file at /swagger.yaml
        self.router.add_api_route("/swagger.yaml", self.serve_swagger_yaml, methods=["GET"])

        # Redirect from / to /api/docs
        self.router.add_api_route("/", self.redirect_to_docs, methods=["GET"])

    async def serve_swagger_yaml(self):
        """
        Handler method for serving the swagger.yaml file.

        Returns:
            FileResponse: The swagger.yaml file served as a YAML file.
        """
        try:
            swagger_loader = SwaggerLoader("swagger.yaml")
            self.logger.debug(f"Serving swagger.yaml from path: {swagger_loader.file_path()}")
            return FileResponse(swagger_loader.file_path(), media_type='application/x-yaml')
        except Exception as e:
            self.logger.error(f"Error serving swagger.yaml: {str(e)}")
            raise HTTPException(status_code=500, detail="An error occurred while serving the swagger.yaml file")

    async def redirect_to_docs(self):
        """
        Redirects requests from the root URL (/) to /api/docs.

        Returns:
            RedirectResponse: A redirection to the Swagger UI at /api/docs.
        """
        return RedirectResponse(url='/api/docs')


