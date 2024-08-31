import logging
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
import uuid
from jsonschema import validate, ValidationError
from ..models.prompts import Prompt
from ..utils.swagger_loader import SwaggerLoader
from ..db.base import async_session_maker, Base
from ..config.settings import Settings

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

router = APIRouter()
settings = Settings()


# Dependency to get the database session
async def get_db():
    async with async_session_maker() as session:
        yield session


@router.get("/prompt", tags=["prompts"])
async def get_prompts(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Prompt).order_by(Prompt.timestamp.desc()))
    prompts = result.scalars().all()
    return [prompt.to_dict() for prompt in prompts]


@router.post("/prompt", tags=["prompts"])
async def create_prompt(prompt: dict, db: AsyncSession = Depends(get_db)):
    try:
        # Validate the input data against the JSON schema
        validate(instance=prompt, schema=SwaggerLoader("swagger.yaml").get_component_schema("Prompt"))

        # Ensure 'user' is converted to a UUID if it isn't already
        prompt['user'] = uuid.UUID(prompt['user']) if isinstance(prompt['user'], str) else prompt['user']

        result = await db.execute(
            select(Prompt).filter_by(prompt=prompt['prompt'], user=prompt['user'])
        )
        existing_prompt = result.scalars().first()

        if existing_prompt:
            return existing_prompt.to_dict()

        new_prompt = Prompt(**prompt)
        db.add(new_prompt)
        await db.commit()
        await db.refresh(new_prompt)

        return new_prompt.to_dict()

    except ValidationError as validation_error:
        # Log the error with detailed information
        logger.error(f"Validation error while creating prompt: {validation_error.message}")
        # Return an HTTP 400 response with the validation error message
        raise HTTPException(status_code=400, detail=f"Validation error: {validation_error.message}")

    except Exception as e:
        # Log any unexpected errors
        logger.error(f"Unexpected error while creating prompt: {str(e)}")
        await db.rollback()
        raise HTTPException(status_code=500, detail="An unexpected error occurred")


    except ValidationError as validation_error:
        # Log the error with detailed information
        logger.error(f"Validation error while creating prompt: {validation_error.message}")
        # Return an HTTP 400 response with the validation error message
        raise HTTPException(status_code=400, detail=f"Validation error: {validation_error.message}")

    except Exception as e:
        # Log any unexpected errors
        logger.error(f"Unexpected error while creating prompt: {str(e)}")
        await db.rollback()
        raise HTTPException(status_code=500, detail="An unexpected error occurred")


@router.delete("/prompt/{prompt_id}", tags=["prompts"])
async def delete_prompt(prompt_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    try:
        prompt = await db.get(Prompt, prompt_id)
        if prompt:
            await db.delete(prompt)
            await db.commit()
            return {"status": "Prompt deleted successfully"}
        else:
            raise HTTPException(status_code=404, detail=f"Prompt with id {prompt_id} not found")

    except Exception as e:
        logger.error(f"Unexpected error while deleting prompt: {str(e)}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred")


