from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import StreamingResponse
import asyncio
import json
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Any, Dict, Type, Optional
from pydantic import BaseModel, Field
from ..config.settings import Settings
from ..clients.openai_client import OpenAIClient
from ..clients.anthropic_client import AnthropicClient
from ..db.base import async_session_maker
from ..models.openai_model import OpenaiModel
from ..models.anthropic_model import AnthropicModel
import logging
import uuid
from ..models.generation_request import GenerationRequest
router = APIRouter()
settings = Settings()

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize clients
openai_client = OpenAIClient(api_key=settings.get("default").get("API_KEY_OPEN_AI"))
anthropic_client = AnthropicClient(api_key=settings.get("default").get("API_KEY_ANTHROPIC"))

registered_methods = ['fetch_completion', 'chat_completion', 'generate_image']
clients = {
    'openai': openai_client,
    'anthropic': anthropic_client,
}

MODEL_CLASS_MAP: Dict[str, Type] = {
    "openai": OpenaiModel,
    "anthropic": AnthropicModel,
}


class ModelNotFoundException(Exception):
    def __init__(self, platform: str):
        self.platform = platform
        super().__init__(f"Model class for platform '{platform}' not found")


class ModelConfig(BaseModel):
    platform: str = Field(..., example="openai", description="The AI platform to use")
    model: str = Field(..., example="gpt-3.5-turbo", description="The specific model to use")
    temperature: float = Field(0.7, ge=0, le=1, example=0.7, description="Controls randomness in output")
    max_tokens: int = Field(100, gt=0, example=100, description="Maximum number of tokens to generate")
    model_id: Optional[str] = Field(None, description="Unique identifier for the model (if applicable)")
    object: Optional[str] = Field(None, description="Object type (if applicable)")


async def get_db():
    async with async_session_maker() as session:
        yield session


def get_model_class(platform: str):
    model_class = MODEL_CLASS_MAP.get(platform)
    if model_class is None:
        raise ModelNotFoundException(platform)
    return model_class


def validate_models_and_clients(models: List[ModelConfig], method_name: str) -> List[Any]:
    valid_models = []
    for model_data in models:
        platform = model_data.platform
        try:
            model_class = get_model_class(platform)
        except ModelNotFoundException as e:
            logger.error(str(e))
            raise HTTPException(status_code=400, detail=str(e))

        platform_client = clients.get(platform)
        if not platform_client:
            raise HTTPException(status_code=400, detail=f"Client for platform '{platform}' not supported")

        if not hasattr(platform_client, method_name):
            raise HTTPException(status_code=400, detail=f"Method '{method_name}' not found for platform '{platform}'")

        model_dict = model_data.dict(exclude_none=True)

        # Ensure 'id' is correctly set for OpenAI models
        if platform == "openai":
            if not model_dict.get("id"):
                if model_dict.get("model_id"):
                    model_dict["id"] = model_dict["model_id"]
                elif model_dict.get("model"):
                    model_dict["id"] = model_dict["model"]
                else:
                    raise HTTPException(status_code=400, detail="Either 'model_id' or 'model' must be provided to set 'id' for OpenAI models.")

        # Ensure 'id' is correctly set for Anthropic models
        if platform == "anthropic":
            if not model_dict.get("id"):
                if model_dict.get("model_id"):
                    model_dict["id"] = model_dict["model_id"]
                elif model_dict.get("model"):
                    model_dict["id"] = model_dict["model"]
                else:
                    raise HTTPException(status_code=400, detail="Either 'model_id' or 'model' must be provided to set 'id' for Anthropic models.")

        try:
            model_instance = model_class(**model_dict)
        except ValueError as e:
            logger.error(f"Error creating model instance: {str(e)}")
            raise HTTPException(status_code=400, detail=f"Invalid model configuration for {platform}: {str(e)}")

        valid_models.append((model_instance, platform_client, getattr(platform_client, method_name)))

    return valid_models


def validate_request(models: List[ModelConfig], method_name: str, prompt_id: str):
    if not models:
        raise HTTPException(status_code=400, detail="The 'models' list cannot be empty.")
    if not prompt_id:
        raise HTTPException(status_code=400, detail="The 'prompt_id' cannot be empty.")
    if method_name not in registered_methods:
        raise HTTPException(status_code=400, detail=f"The method '{method_name}' is not allowed.")


@router.post("/stream", tags=["generation"])
async def stream_route(request: GenerationRequest, db: AsyncSession = Depends(get_db)):
    """
    Stream AI-generated content based on the provided prompt and model configurations.

    This endpoint accepts a GenerationRequest object containing:
    - A list of model configurations
    - A prompt for content generation
    - A unique prompt ID
    - The method name for generation (e.g., 'chat_completion')

    It returns a streaming response with the generated content.
    """
    logger.info("Incoming request to /stream:")
    logger.info(json.dumps(request.dict(), indent=2))
    logger.info("=" * 50)

    try:
        validate_request(request.models, request.method_name, request.prompt_id)
        valid_models = validate_models_and_clients(request.models, request.method_name)
    except HTTPException as e:
        logger.error(str(e))
        raise e
    except ModelNotFoundException as e:
        logger.error(str(e))
        raise HTTPException(status_code=400, detail=str(e))

    async def generate():
        tasks = []
        for model, client, method in valid_models:
            async_task = method(model, request.prompt, request.prompt_id)
            task = asyncio.create_task(async_task)
            tasks.append(task)

        for completed_task in asyncio.as_completed(tasks):
            try:
                async_gen = await completed_task
                async for result in async_gen:
                    yield result  # Result is already in bytes
            except Exception as e:
                logger.error(f"Error during task execution: {str(e)}")
                yield json.dumps({"error": str(e)}).encode('utf-8') + b'\n'

    return StreamingResponse(generate(), media_type='application/json')
