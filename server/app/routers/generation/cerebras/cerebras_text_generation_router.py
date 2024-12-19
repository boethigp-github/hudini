import logging
from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import StreamingResponse
import asyncio
from typing import List, Any, Dict, Type, Optional
from pydantic import BaseModel, Field

from server.app.clients.cerebras.cerebras_client import CerebrasClient
from server.app.config.settings import Settings
from server.app.db.base import async_session_maker
from server.app.models.generation.cerebras_model import CerebrasModel
from server.app.models.generation.generation_request import GenerationRequest
from server.app.models.generation.success_generation_model import SuccessGenerationModel
from server.app.utils.auth import auth
from server.app.services.gripsbox_service import add_gripsbox_content_to_llm_context
from server.app.models.users.user import User
import json
from server.app.utils.user_context_util import get_user_context

router = APIRouter()
settings = Settings()

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize clients
cerebras_client = CerebrasClient(api_key=settings.get("default").get("API_KEY_CEREBRAS"))


registered_methods = ['fetch_completion', 'chat_completion']
clients = {
    'cerebras': cerebras_client,
}

MODEL_CLASS_MAP: Dict[str, Type] = {
    "cerebras": CerebrasModel,
}


class ModelNotFoundException(Exception):
    def __init__(self, platform: str):
        self.platform = platform
        super().__init__(f"Model class for platform '{platform}' not found")


class ModelConfig(BaseModel):
    platform: str = Field(..., example="cerebras", description="The AI platform to use.")
    model: str = Field(..., example="llama", description="The specific model to use.")
    temperature: float = Field(0.7, ge=0, le=1, example=0.7, description="Controls randomness in output.")
    max_tokens: int = Field(100, gt=0, example=100, description="Maximum number of tokens to generate.")
    model_id: Optional[str] = Field(None, description="Unique identifier for the model (if applicable).")
    object: Optional[str] = Field(None, description="Object type (if applicable).")


async def get_db():
    async with async_session_maker() as session:
        yield session


def get_model_class(platform: str):
    model_class = MODEL_CLASS_MAP.get(platform)
    if model_class is None:
        raise ModelNotFoundException(platform)
    return model_class


def set_model_id(platform: str, model_dict: dict) -> None:
    """
    Sets the 'id' field in the model_dict for the specified platform.
    Raises an HTTPException if neither 'model_id' nor 'model' are provided.
    """
    if not model_dict.get("id"):
        model_dict["id"] = model_dict.get("model_id") or model_dict.get("model")
        if not model_dict["id"]:
            raise HTTPException(
                status_code=400,
                detail=f"Either 'model_id' or 'model' must be provided to set 'id' for {platform.capitalize()} models."
            )


def validate_models_and_clients(models: List[ModelConfig], method_name: str) -> List[Any]:
    valid_models = []
    for model_data in models:
        platform = model_data.platform

        # Get the model class
        try:
            model_class = get_model_class(platform)
        except ModelNotFoundException as e:
            logger.error(str(e))
            raise HTTPException(status_code=400, detail=str(e))

        # Validate platform client
        platform_client = clients.get(platform)
        if not platform_client:
            raise HTTPException(status_code=400, detail=f"Client for platform '{platform}' not supported")

        if not hasattr(platform_client, method_name):
            raise HTTPException(status_code=400, detail=f"Method '{method_name}' not found for platform '{platform}'")

        # Validate model configuration
        model_dict = model_data.model_dump(exclude_none=True)
        set_model_id(platform, model_dict)  # Simplified logic here

        # Create model instance
        try:
            model_instance = model_class(**model_dict)
        except ValueError as e:
            logger.error(f"Error creating model instance: {str(e)}")
            raise HTTPException(status_code=400, detail=f"Invalid model configuration for {platform}: {str(e)}")

        # Append valid models
        valid_models.append((model_instance, platform_client, getattr(platform_client, method_name)))

    return valid_models




@router.post(
    "/stream/cerebras",
    response_model=SuccessGenerationModel,
    tags=["generation"],
    summary="Stream Cerebras Models",
    description=(
            "This endpoint streams AI-generated content based on the provided prompt and model configurations. "
            "It supports models from OpenAI and Anthropic platforms. "
            "The request must specify the platform and model configuration in the `models` field. "
            "The method specified in the `method_name` field will be invoked on the selected models. "
            "If the configuration is invalid or the platform is not supported, a `400 Bad Request` error is raised."
    ),
)
@router.post(
    "/stream/cerebras",
    response_model=SuccessGenerationModel,
    tags=["generation"],
    summary="Stream Cerebras",
    description=(
        "This endpoint streams AI-generated content based on the provided prompt and model configurations. "
        "It supports models from Cerebras platforms. "
        "The request must specify the platform and model configuration in the `models` field. "
        "The method specified in the `method_name` field will be invoked on the selected models. "
        "If the configuration is invalid or the platform is not supported, a `400 Bad Request` error is raised."
    ),
)
async def stream_route(request: GenerationRequest, user: User = Depends(auth),db: Any = Depends(get_db)):
    """
    Stream AI-generated content based on the provided prompt and model configurations.

    - **request**: A `GenerationRequest` object containing the models, method name, and other parameters for generation.
    - **db**: Database session dependency.

    This endpoint validates the model configurations and method name, then streams the generated content
    as a JSON response. It supports concurrent model generation and handles errors related to invalid configurations.

    **Returns**: A streaming JSON response with the generation result.
    """
    logger.info("Incoming request to /stream/cerebras:")
    logger.info(request.model_dump_json())
    logger.info("=" * 50)

    # Fetch user context from the database
    user_context = await get_user_context(thread_id=1, get_db=get_db)

    try:
        gripsbox_context_messages = await add_gripsbox_content_to_llm_context(user)
        # Safely join content messages
        gripsbox_content = " ".join([msg.content for msg in gripsbox_context_messages])

    except Exception as e:
        # Log the error if necessary
        gripsbox_content = ""


    # Combine user context and Gripsbox content into a single context
    combined_context = user_context + " " + gripsbox_content



    # Validate models and clients
    valid_models = validate_models_and_clients(request.models, request.method_name)

    async def generate():
        tasks = []

        for model, client, method in valid_models:
            # Pass the combined context as a parameter to fetch_completion
            async_task = method(model, request.prompt, request.id, context=combined_context,   db=db, user_uuid=str(user.uuid) )
            task = asyncio.create_task(async_task)
            tasks.append(task)

        for completed_task in asyncio.as_completed(tasks):
            async_gen = await completed_task
            async for result in async_gen:
                if isinstance(result, bytes):
                    result = result.decode('utf-8')

                # Deserialize using Pydantic model's model_validate
                success_model = SuccessGenerationModel.model_validate(json.loads(result))
                # Serialize using model_dump_json
                yield success_model.model_dump_json().encode('utf-8') + b'\n'

    return StreamingResponse(generate(), media_type='application/json')

