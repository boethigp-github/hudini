import logging
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from server.app.models.usercontext.user_context import UserContextModel
from server.app.models.usercontext.usercontext_post_request_model import UserContextPostRequestModel
from server.app.models.usercontext.usercontext_post_response_model import UserContextResponseModel
from server.app.db.base import async_session_maker
from fastapi.encoders import jsonable_encoder
from datetime import datetime
from typing import List
logger = logging.getLogger(__name__)
router = APIRouter()


async def get_db():
    async with async_session_maker() as session:
        yield session


from pydantic import ValidationError

from pydantic import ValidationError

@router.post("/usercontext", tags=["usercontext"], response_model=List[UserContextResponseModel])
async def save_user_context(user_contexts: List[UserContextPostRequestModel], db: AsyncSession = Depends(get_db)):
    try:
        logger.debug(f"Received request to save user contexts: {user_contexts}")

        saved_contexts = []
        for user_context in user_contexts:
            # Check if context_data is empty
            if not user_context.prompt.context_data:
                raise HTTPException(status_code=400, detail="Context data must not be empty")

            # Check if the record already exists
            existing_context = await db.get(UserContextModel, user_context.uuid)

            if existing_context:
                # Update existing record
                existing_context.user = user_context.user
                existing_context.thread_id = user_context.thread_id
                existing_context.context_data = jsonable_encoder(user_context.dict())
                existing_context.updated = datetime.now()  # Correct usage of datetime
                new_user_context = existing_context
            else:
                # Create new record
                new_user_context = UserContextModel(
                    uuid=user_context.uuid,
                    user=user_context.user,
                    thread_id=user_context.thread_id,
                    context_data=jsonable_encoder(user_context.dict()),
                    updated=datetime.now()  # Correct usage of datetime
                )
                db.add(new_user_context)

            await db.commit()
            await db.refresh(new_user_context)

            saved_contexts.append(UserContextResponseModel(**new_user_context.to_dict()))

        return saved_contexts

    except ValidationError as e:
        logger.error(f"Validation error: {e.errors()}")
        await db.rollback()
        raise HTTPException(status_code=422, detail={"errors": e.errors(), "message": "Validation failed"})
    except HTTPException as e:
        logger.error(f"HTTP error: {str(e)}")
        await db.rollback()
        raise
    except Exception as e:
        logger.error(f"Error saving user context: {str(e)}")
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"An error occurred while saving the user context: {str(e)}")


@router.get("/usercontext", tags=["usercontext"], response_model=List[UserContextResponseModel])
async def get_user_contexts(user: str, thread_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(UserContextModel)
        .where(
            UserContextModel.user == user,
            UserContextModel.thread_id == thread_id
        )
        .order_by(UserContextModel.created.asc())
    )
    user_contexts = result.scalars().all()

    if not user_contexts:
        raise HTTPException(status_code=404, detail="No contexts found for the given user and thread_id")

    return [UserContextResponseModel(**context.to_dict()) for context in user_contexts]


@router.delete("/usercontext/{thread_id}", tags=["usercontext"])
async def delete_user_context(thread_id: int, db: AsyncSession = Depends(get_db)):
    try:
        # Delete all user_context records where thread_id matches
        result = await db.execute(
            select(UserContextModel).where(UserContextModel.thread_id == thread_id)
        )
        user_contexts = result.scalars().all()

        if not user_contexts:
            raise HTTPException(status_code=404, detail=f"No user contexts found for thread_id {thread_id}")

        # Iterate and delete all matching user_contexts
        for user_context in user_contexts:
            await db.delete(user_context)

        await db.commit()

        return {"status": f"All user contexts with thread_id {thread_id} deleted successfully"}

    except Exception as e:
        logger.error(f"Error occurred while deleting user contexts: {str(e)}")
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")

