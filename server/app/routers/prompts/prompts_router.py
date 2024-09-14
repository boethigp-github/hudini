import logging
from fastapi import APIRouter, HTTPException, Depends, status, FastAPI
from fastapi.security import APIKeyHeader
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from jsonschema import ValidationError
from server.app.models.prompts.prompts import Prompt
from server.app.db.base import async_session_maker
from server.app.config.settings import Settings
from typing import List
from server.app.models.prompts.prompt_post_response_model import PromptPostResponseModel
from server.app.models.prompts.prompt_post_request_model import PromptPostRequestModel
from server.app.utils.check_user_session import check_user_session
from uuid import UUID
import secrets

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = FastAPI()
router = APIRouter()

settings = Settings()

# Fake users database with API keys (replace with a real DB in production)
fake_users_db = {
    "apiuser1": {
        "username": "apiuser1",
        "api_key": "d393fcfd8a447135675e09f8741fe0f8be8ca52d3b30d49c4b4a7e6596e66c03"
    },
    "apiuser2": {
        "username": "apiuser2",
        "api_key": "076a23880d4db7b8754b92873eb49be95fbe33d2040f7f0faee7c9eb3c970de1"
    }
}


# Dependency to get the database session
async def get_db():
    async with async_session_maker() as session:
        yield session


# Security header for API key
api_key_header = APIKeyHeader(name="X-API-Key")


# Function to verify API key
def get_api_user(api_key: str = Depends(api_key_header)):
    for user in fake_users_db.values():
        if user["api_key"] == api_key:
            return user
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid API Key",
        headers={"WWW-Authenticate": "API-Key"},
    )


# Route to get prompts (no authentication required for this route)
@router.get("/prompts", response_model=List[PromptPostResponseModel], tags=["prompts"])
async def get_prompts(db: AsyncSession = Depends(get_db)):
    try:
        result = await db.execute(select(Prompt).order_by(Prompt.created.desc()))
        prompts = result.scalars().all()
        return prompts  # FastAPI will automatically convert SQLAlchemy models to Pydantic models
    except Exception as e:
        logger.error(f"Error retrieving prompts: {str(e)}")
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred {str(e)}")


# Route to create a prompt (authentication via API key or Google OAuth required)
@router.post("/prompts", response_model=PromptPostResponseModel, status_code=status.HTTP_201_CREATED, tags=["prompts"])
async def create_prompt(
        prompt: PromptPostRequestModel,
        db: AsyncSession = Depends(get_db),
        user: dict = Depends(get_api_user)  # Authenticate using API key
):
    try:
        # Log the incoming data
        logger.debug(f"Incoming prompt data: {prompt} from user {user['username']}")

        # Check for existing prompt
        result = await db.execute(
            select(Prompt).filter_by(prompt=prompt.prompt, user=prompt.user)
        )
        existing_prompt = result.scalars().first()

        if existing_prompt:
            logger.info(f"Prompt already exists: {existing_prompt}")
            return PromptPostResponseModel.model_validate(existing_prompt)

        # Log data to be saved
        logger.debug(f"Creating new prompt with data: {prompt.model_dump()}")

        # Create and save new prompt
        new_prompt = Prompt(**prompt.model_dump())
        db.add(new_prompt)
        await db.commit()
        await db.refresh(new_prompt)

        # Log the newly created prompt
        logger.debug(f"Prompt created successfully: {new_prompt}")

        return PromptPostResponseModel.model_validate(new_prompt)

    except ValidationError as validation_error:
        logger.error(f"Validation error while creating prompt: {validation_error}")
        raise HTTPException(status_code=400, detail=f"Validation error: {validation_error}")

    except Exception as e:
        logger.error(f"Unexpected error while creating prompt: {str(e)}")
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred {str(e)}")


# Route to delete a prompt (authentication via API key or Google OAuth required)
@router.delete("/prompts/{uuid}", tags=["prompts"])
async def delete_prompt(uuid: UUID, db: AsyncSession = Depends(get_db), user: dict = Depends(get_api_user)):
    prompt = await db.get(Prompt, uuid)
    if prompt:
        await db.delete(prompt)
        await db.commit()
        logger.info(f"Prompt deleted successfully by {user['username']}: id={uuid}")
        return {"status": "Prompt deleted successfully"}
    else:
        logger.warning(f"Prompt not found: id={uuid}")
        raise HTTPException(status_code=404, detail=f"Prompt with id {id} not found")


# Custom OpenAPI Schema to include API Key Authentication for Swagger UI
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = app.openapi()

    # Security schema definition for API Key
    openapi_schema["components"]["securitySchemes"] = {
        "ApiKeyAuth": {
            "type": "apiKey",
            "in": "header",
            "name": "X-API-Key"  # Der Header, in dem der API-Schlüssel erwartet wird
        }
    }

    # Füge die API-Key-Authentifizierung für alle Endpunkte hinzu
    openapi_schema["security"] = [{"ApiKeyAuth": []}]

    app.openapi_schema = openapi_schema
    return app.openapi_schema


# Override FastAPI's default OpenAPI schema with custom schema
app.openapi = custom_openapi

# Include the router in the FastAPI app
app.include_router(router)
