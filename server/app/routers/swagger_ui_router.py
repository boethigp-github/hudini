from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse, RedirectResponse
import logging
from ..utils.swagger_loader import SwaggerLoader

router = APIRouter()
logger = logging.getLogger("hudini_logger")

@router.get("/swagger.yaml", tags=["swagger"])
async def serve_swagger_yaml():
    """
    Handler method for serving the swagger.yaml file.

    Returns:
        FileResponse: The swagger.yaml file served as a YAML file.
    """
    try:
        swagger_loader = SwaggerLoader("swagger.yaml")
        logger.debug(f"Serving swagger.yaml from path: {swagger_loader.file_path()}")
        return FileResponse(swagger_loader.file_path(), media_type='application/x-yaml')
    except Exception as e:
        logger.error(f"Error serving swagger.yaml: {str(e)}")
        raise HTTPException(status_code=500, detail="An error occurred while serving the swagger.yaml file")

@router.get("/", tags=["swagger"])
async def redirect_to_docs():
    """
    Redirects requests from the root URL (/) to /api/docs.

    Returns:
        RedirectResponse: A redirection to the Swagger UI at /api/docs.
    """
    return RedirectResponse(url='/api/docs')

@router.get("/api/docs", tags=["swagger"])
async def serve_swagger_yaml():
    """
    Handler method for serving the swagger.yaml file.

    Returns:
        FileResponse: The swagger.yaml file served as a YAML file.
    """
    try:
        swagger_loader = SwaggerLoader("swagger.yaml")
        logger.debug(f"Serving swagger.yaml from path: {swagger_loader.file_path()}")
        return FileResponse(swagger_loader.file_path(), media_type='application/x-yaml')
    except Exception as e:
        logger.error(f"Error serving swagger.yaml: {str(e)}")
        raise HTTPException(status_code=500, detail="An error occurred while serving the swagger.yaml file")