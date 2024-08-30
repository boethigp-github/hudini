from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List, Optional
from ..models.prompts import Prompt
from ..db.base import async_session_maker
from ..config.settings import Settings

router = APIRouter()
settings = Settings()


# Dependency
async def get_db():
    async with async_session_maker() as session:
        yield session


@router.get("/prompt", tags=["prompts"], response_model=List[dict])
async def get_prompts(
        limit: int = Query(100, ge=1, le=1000),
        user: Optional[str] = None,
        status: Optional[str] = None,
        db: AsyncSession = Depends(get_db)
):
    try:
        query = select(Prompt).order_by(Prompt.timestamp.desc())

        # Apply filters if provided
        if user:
            query = query.filter(Prompt.user == user)
        if status:
            query = query.filter(Prompt.status == status)

        # Apply limit
        query = query.limit(limit)

        result = await db.execute(query)
        prompts = result.scalars().all()

        return [prompt.to_dict() for prompt in prompts]

    except Exception as e:
        # Log the error here if you have a logging system set up
        raise HTTPException(status_code=500, detail=f"An error occurred while fetching prompts: {str(e)}")


# You might want to add a separate endpoint for getting a single prompt by ID
@router.get("/prompt/{prompt_id}", tags=["prompts"], response_model=dict)
async def get_prompt(prompt_id: str, db: AsyncSession = Depends(get_db)):
    try:
        result = await db.execute(select(Prompt).filter(Prompt.id == prompt_id))
        prompt = result.scalar_one_or_none()

        if prompt is None:
            raise HTTPException(status_code=404, detail="Prompt not found")

        return prompt.to_dict()

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred while fetching the prompt: {str(e)}")