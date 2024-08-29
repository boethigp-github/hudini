from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
import uuid
from jsonschema import validate, ValidationError
from ..models.prompts import Prompt
from ..utils.swagger_loader import SwaggerLoader
from ..db.base import async_session_maker, Base
from ..config.settings import Settings

router = APIRouter()
settings = Settings()

# Dependency
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
        validate(instance=prompt, schema=SwaggerLoader("swagger.yaml").get_component_schema("Prompt"))

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
        raise HTTPException(status_code=400, detail=validation_error.message)
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail="An unexpected error occurred")

@router.delete("/prompt/{prompt_id}", tags=["prompts"])
async def delete_prompt(prompt_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    prompt = await db.get(Prompt, prompt_id)
    if prompt:
        await db.delete(prompt)
        await db.commit()
        return {"status": "Prompt deleted successfully"}
    else:
        raise HTTPException(status_code=404, detail=f"Prompt with id {prompt_id} not found")

@router.patch("/prompt/{prompt_id}", tags=["prompts"])
async def update_prompt(prompt_id: uuid.UUID, prompt: dict, db: AsyncSession = Depends(get_db)):
    try:
        validate(instance=prompt, schema=SwaggerLoader("swagger.yaml").get_component_schema("Prompt"))

        existing_prompt = await db.get(Prompt, prompt_id)
        if not existing_prompt:
            raise HTTPException(status_code=404, detail="Prompt not found")

        for key, value in prompt.items():
            setattr(existing_prompt, key, value)

        await db.commit()
        await db.refresh(existing_prompt)

        return existing_prompt.to_dict()
    except ValidationError as validation_error:
        raise HTTPException(status_code=400, detail=validation_error.message)
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail="An unexpected error occurred")