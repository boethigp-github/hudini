import logging
import os
from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from server.app.config.settings import Settings
from server.app.db.base import async_session_maker
from server.app.models.generation.generation_request import GenerationRequest
from server.app.clients.google_ai_client import GoogleAICLient
import google.generativeai as genai
from server.app.models.generation.success_generation_model import SuccessGenerationModel

# Configure the Google Generative AI SDK
genai.configure(api_key=os.environ["API_KEY_GEMINI"])

router = APIRouter()
settings = Settings()

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def get_db():
    async with async_session_maker() as session:
        yield session

@router.post("/stream/google-ai", response_model=SuccessGenerationModel, tags=["generation"])
async def stream_google_ai_route(request: GenerationRequest, db: AsyncSession = Depends(get_db)):
    logger.info("Incoming request to /stream/google-ai:")
    logger.info(request.model_dump_json())
    logger.info("=" * 50)

    if not request.models or len(request.models) == 0:
        raise HTTPException(status_code=400, detail="No models provided in the request.")

    model_config = request.models[0]  # Assuming you're using the first model in the list

    google_ai_client=GoogleAICLient(api_key=settings.get("default").get("API_KEY_GOOGLE_AI"))

    return StreamingResponse(google_ai_client.generate(model_config, request), media_type='application/json')
