import logging
import json
from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, Field
from typing import List, Optional
from server.app.config.settings import Settings
from server.app.clients.openai.openai_image_generation_client import OpenAIImageGenerationClient as OpenAIClient
from server.app.db.base import async_session_maker
from server.app.models.generation.success_generation_model import SuccessGenerationModel, Completion

router = APIRouter()
settings = Settings()

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize OpenAI client
openai_client = OpenAIClient(api_key=settings.get("default").get("API_KEY_OPEN_AI"))

# Sample prompt for testing
SAMPLE_PROMPT = "A serene landscape with a calm lake reflecting a snow-capped mountain at sunset"

class ImageGenerationRequest(BaseModel):
    prompt: Optional[str] = Field(None, description="The prompt for image generation. If not provided, a sample prompt will be used.")
    n: int = Field(1, ge=1, le=10, description="Number of images to generate")
    size: str = Field("600x600", description="Size of the generated images")

async def get_db():
    async with async_session_maker() as session:
        yield session

@router.post(
    "/generate/image",
    response_model=SuccessGenerationModel,
    tags=["image_generation"],
    summary="Generate images using DALL-E 2",
    description="This endpoint generates images based on the provided prompt (or a sample prompt) using OpenAI's DALL-E 2 model.",
)
async def generate_image(request: ImageGenerationRequest, db: AsyncSession = Depends(get_db)):
    logger.info("Incoming request to /generate/image:")
    logger.info(request.model_dump_json())
    logger.info("=" * 50)

    # Use the sample prompt if no prompt is provided
    prompt = request.prompt or SAMPLE_PROMPT
    logger.info(f"Using prompt: {prompt}")

    try:
        response = await openai_client.create_image(
            prompt=prompt,
            n=request.n,
            size=request.size
        )

        # Extract image URLs from the response
        image_urls = [image['url'] for image in response['data']]

        result = SuccessGenerationModel(
            id=str(response['created']),
            object="image_generation",
            created=response['created'],
            model="dall-e-2",
            choices=[
                {
                    "text": f"Image URL: {url}",
                    "index": idx,
                    "logprobs": None,
                    "finish_reason": "stop"
                }
                for idx, url in enumerate(image_urls)
            ],
            usage={
                "prompt_tokens": len(prompt.split()),
                "completion_tokens": 0,
                "total_tokens": len(prompt.split()),
                "started": response.get('started', response['created']),
                "ended": response.get('ended', response['created'])
            },
            completion=Completion(
                id=f"completion-{response['created']}",
                object="text_completion",
                created=response['created'],
                model="dall-e-2",
                choices=[
                    {
                        "message": {
                            "role": "assistant",
                            "content": json.dumps({
                                "message": "Image generation completed successfully",
                                "image_urls": image_urls
                            }),
                            "refusal": None
                        },
                        "index": 0,
                        "logprobs": None,
                        "finish_reason": "stop"
                    }
                ],
                usage={
                    "prompt_tokens": len(prompt.split()),
                    "completion_tokens": 0,
                    "total_tokens": len(prompt.split()),
                    "started": response.get('started', response['created']),
                    "ended": response.get('ended', response['created'])
                },
                system_fingerprint=None
            )
        )

        return JSONResponse(content=result.model_dump())

    except Exception as e:
        logger.error(f"Error in image generation: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Image generation failed: {str(e)}")

# Test route to quickly generate an image using the sample prompt
@router.get(
    "/test/generate/image",
    response_model=SuccessGenerationModel,
    tags=["image_generation"],
    summary="Test image generation using a sample prompt",
    description="This endpoint generates an image using a predefined sample prompt with DALL-E 2.",
)
async def test_generate_image(db: AsyncSession = Depends(get_db)):
    test_request = ImageGenerationRequest(n=1, size="1024x1024")
    return await generate_image(test_request, db)