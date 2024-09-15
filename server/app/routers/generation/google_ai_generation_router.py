import logging
from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from server.app.config.settings import Settings
from server.app.db.base import async_session_maker
from server.app.models.generation.generation_request import GenerationRequest
from server.app.clients.googleai.google_ai_client import GoogleAICLient
from server.app.models.generation.success_generation_model import SuccessGenerationModel
from server.app.utils.auth import auth
router = APIRouter()
settings = Settings()

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def get_db():
    async with async_session_maker() as session:
        yield session

@router.post(
    "/stream/google-ai",
    response_model=SuccessGenerationModel,
    tags=["generation"],
    summary="Stream Google AI Model Generation",
    description=(
        "This endpoint streams the output from the Google AI model generation. "
        "It accepts a `GenerationRequest` containing the models to be used for generation. "
        "If the request does not include any models, a `400 Bad Request` error is raised. "
        "The endpoint returns a streaming JSON response that contains the generated output."
    ),
)
async def stream_google_ai_route(request: GenerationRequest, db: AsyncSession = Depends(get_db), _: str = Depends(auth)):
    """
    Stream output from the Google AI model based on the provided generation request.

    - **request**: A `GenerationRequest` object containing the models and other parameters for generation.
    - **db**: Database session dependency.

    This endpoint interacts with the GoogleAICLient to generate text outputs from the specified models.
    It logs the request details and handles errors if no models are provided in the request.

    **Returns**: A streaming JSON response with the generation result.
    """
    logger.info("Incoming request to /stream/google-ai:")
    logger.info(request.model_dump_json())
    logger.info("=" * 50)

    if not request.models or len(request.models) == 0:
        raise HTTPException(status_code=400, detail="No models provided in the request.")

    model_config = request.models[0]  # Assuming you're using the first model in the list

    google_ai_client = GoogleAICLient(api_key=settings.get("default").get("API_KEY_GOOGLE_AI"))

    return StreamingResponse(google_ai_client.generate(model_config, request), media_type='application/json')
