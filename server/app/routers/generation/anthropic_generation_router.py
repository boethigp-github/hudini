import logging
from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from server.app.config.settings import Settings
from server.app.db.base import async_session_maker
from server.app.models.generation.generation_request import GenerationRequest
from server.app.clients.anthropic_client import AnthropicClient
from server.app.models.generation.success_generation_model import SuccessGenerationModel

router = APIRouter()
settings = Settings()

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def get_db():
    async with async_session_maker() as session:
        yield session

@router.post("/stream/anthropic", response_model=SuccessGenerationModel, tags=["generation"])
async def stream_anthropic_route(request: GenerationRequest, db: AsyncSession = Depends(get_db)):
    logger.info("Incoming request to /stream/anthropic:")
    logger.info(request.model_dump_json())
    logger.info("=" * 50)

    if not request.models or len(request.models) == 0:
        raise HTTPException(status_code=400, detail="No models provided in the request.")

    client = AnthropicClient(api_key=settings.get("default").get("API_KEY_ANTHROPIC"))

    return StreamingResponse(client.generate(request.models, request), media_type='application/json')
