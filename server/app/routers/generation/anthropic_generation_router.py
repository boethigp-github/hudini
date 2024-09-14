import logging
from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from server.app.config.settings import Settings
from server.app.db.base import async_session_maker
from server.app.models.generation.generation_request import GenerationRequest
from server.app.clients.anthropic.anthropic_client import AnthropicClient
from server.app.models.generation.success_generation_model import SuccessGenerationModel
from sqlalchemy import select
from server.app.models.usercontext.user_context import UserContextModel
from server.app.utils.check_user_session import check_user_session
import json
router = APIRouter()
settings = Settings()

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def get_db():
    async with async_session_maker() as session:
        yield session


async def get_user_context(db: AsyncSession, thread_id: int = 1) -> str:
    result = await db.execute(
        select(UserContextModel)
        .where(UserContextModel.thread_id == thread_id)
        .order_by(UserContextModel.created.asc())
    )
    user_contexts = result.scalars().all()

    # Extract context_data and convert to string
    context_data_strings = [json.dumps(uc.context_data) for uc in user_contexts]

    # Add "You are a helpful assistant" as the first part of the context
    combined_context = "You are a helpful assistant. " + " ".join(context_data_strings)

    return combined_context

@router.post(
    "/stream/anthropic",
    response_model=SuccessGenerationModel,
    tags=["generation"],
    summary="Stream Anthropic Model Generation",
    description=(
        "This endpoint streams the output from the Anthropic model generation. "
        "It accepts a `GenerationRequest` containing the models to be used for generation. "
        "If the request does not include any models, a `400 Bad Request` error is raised. "
        "The endpoint returns a streaming JSON response that contains the generated output."
    )

)

async def stream_anthropic_route(request: GenerationRequest, db: AsyncSession = Depends(get_db), _: str = Depends(check_user_session)):
    """
    Stream output from the Anthropic model based on the provided generation request.

    - **request**: A `GenerationRequest` object containing the models and other parameters for generation.
    - **db**: Database session dependency.

    This endpoint interacts with the AnthropicClient to generate text outputs from the specified models.
    It logs the request details and handles errors if no models are provided in the request.

    **Returns**: A streaming JSON response with the generation result.
    """
    logger.info("Incoming request to /stream/anthropic:")
    logger.info(request.model_dump_json())
    logger.info("=" * 50)

    if not request.models or len(request.models) == 0:
        raise HTTPException(status_code=400, detail="No models provided in the request.")

    # Fetch user context from the database
    user_context = await get_user_context(db, thread_id=1)

    client = AnthropicClient(api_key=settings.get("default").get("API_KEY_ANTHROPIC"))

    return StreamingResponse(client.generate(request.models, request, context=user_context), media_type='application/json')
