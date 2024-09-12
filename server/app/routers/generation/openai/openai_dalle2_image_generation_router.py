import logging
from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import List, Literal
from openai import OpenAI
from openai.types.images_response import ImagesResponse
from sqlalchemy.ext.asyncio import AsyncSession

# Assuming you have these imports from your existing code
from server.app.config.settings import Settings
from server.app.db.base import async_session_maker

router = APIRouter()
settings = Settings()

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize OpenAI client
client = OpenAI(api_key=settings.get("default").get("API_KEY_OPEN_AI"))

class ImageGenerationRequest(BaseModel):
    prompt: str = Field(..., description="The prompt for image generation")
    n: int = Field(1, ge=1, le=10, description="Number of images to generate")
    size: Literal["1024x1024", "1792x1024", "1024x1792"] = Field("1024x1024", description="Size of the generated images")
    quality: Literal["standard", "hd"] = Field("standard", description="Quality of the generated images")
    style: Literal["vivid", "natural"] = Field("vivid", description="Style of the generated images")

    class Config:
        schema_extra = {
            "example": {
                "prompt": "A serene landscape with a calm lake reflecting a snow-capped mountain at sunset",
                "n": 1,
                "size": "1024x1024",
                "quality": "standard",
                "style": "vivid"
            }
        }

class ImageGenerationResponse(BaseModel):
    created: int
    data: List[dict]

    class Config:
        schema_extra = {
            "example": {
                "created": 1631619392,
                "data": [
                    {
                        "url": "https://example.com/generated_image.png",
                        "revised_prompt": "A breathtaking serene landscape featuring a mirror-like calm lake reflecting the majestic snow-capped mountain peaks, bathed in the warm golden light of a vivid sunset."
                    }
                ]
            }
        }

async def get_db():
    async with async_session_maker() as session:
        yield session

@router.post(
    "/generate/image",
    response_model=ImageGenerationResponse,
    tags=["image_generation"],
    summary="Generate images using DALL-E 3",
    description="This endpoint generates images based on the provided prompt using OpenAI's DALL-E 3 model.",
)
async def generate_image(request: ImageGenerationRequest, db: AsyncSession = Depends(get_db)):
    logger.info("Incoming request to /generate/image:")
    logger.info(request.model_dump_json())
    logger.info("=" * 50)

    try:
        response: ImagesResponse = client.images.generate(
            model="dall-e-3",
            prompt=request.prompt,
            n=request.n,
            size=request.size,
            quality=request.quality,
            style=request.style
        )

        result = ImageGenerationResponse(
            created=response.created,
            data=[{"url": image.url, "revised_prompt": image.revised_prompt} for image in response.data]
        )

        return JSONResponse(content=result.model_dump())

    except Exception as e:
        logger.error(f"Error in image generation: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Image generation failed: {str(e)}")

# Test route to quickly generate an image using a sample prompt
@router.get(
    "/test/generate/image",
    response_model=ImageGenerationResponse,
    tags=["image_generation"],
    summary="Test image generation using a sample prompt",
    description="This endpoint generates an image using a predefined sample prompt with DALL-E 3.",
)
async def test_generate_image(db: AsyncSession = Depends(get_db)):
    test_request = ImageGenerationRequest(
        prompt="A serene landscape with a calm lake reflecting a snow-capped mountain at sunset",
        n=1,
        size="1024x1024",
        quality="standard",
        style="vivid"
    )
    return await generate_image(test_request, db)