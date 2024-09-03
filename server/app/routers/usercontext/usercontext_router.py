import logging
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from server.app.models.usercontext.user_context import UserContextModel
from server.app.models.usercontext.usercontext_post_request import UserContextPostRequestModel
from server.app.models.usercontext.usercontext_response import UserContextResponseModel
from server.app.db.base import async_session_maker
from typing import List


# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

router = APIRouter()

async def get_db():
    async with async_session_maker() as session:
        yield session


def serialize(context_data):
    logger.debug(f"Original context_data: {context_data}")
    return context_data

@router.get("/usercontext", tags=["usercontext"], response_model=List[UserContextResponseModel])
async def get_user_contexts(user: int, thread_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(UserContextModel).where(
            UserContextModel.user == user,
            UserContextModel.thread_id == thread_id
        )
    )
    user_contexts = result.scalars().all()

    if not user_contexts:
        return []

    return [user_context.to_dict() for user_context in user_contexts]

@router.post("/usercontext", tags=["usercontext"], response_model=UserContextResponseModel)
async def save_user_context(user_context: UserContextPostRequestModel, db: AsyncSession = Depends(get_db)):
    logger.debug(f"Received request to save user context: {user_context.model_dump()}")

    try:
        # Convert UUIDs in context_data to strings
        user_context_dict = user_context.model_dump()
        user_context_dict['context_data'] = serialize(user_context_dict['context_data'])

        # Check if a UserContext with the same user and thread_id already exists
        result = await db.execute(
            select(UserContextModel).where(
                UserContextModel.user == user_context.user,
                UserContextModel.thread_id == user_context.thread_id
            )
        )
        existing_user_context = result.scalars().first()

        if existing_user_context:
            logger.info(f"Updating existing user context with user {user_context.user} and thread_id {user_context.thread_id}")
            # Update only the context_data field and updated timestamp
            existing_user_context.context_data = user_context_dict['context_data']
            await db.commit()
            await db.refresh(existing_user_context)
            return UserContextResponseModel.model_validate(existing_user_context)
        else:
            logger.info(f"Creating new user context with user {user_context.user} and thread_id {user_context.thread_id}")
            new_user_context = UserContextModel(**user_context_dict)
            db.add(new_user_context)
            await db.commit()
            await db.refresh(new_user_context)
            return UserContextResponseModel.model_validate(new_user_context)

    except Exception as e:
        logger.error(f"Error occurred while saving user context: {str(e)}")
        await db.rollback()
        raise HTTPException(status_code=500, detail="An unexpected error occurred")


@router.delete("/usercontext/{user_context_id}", tags=["usercontext"])
async def delete_user_context(user_context_id: int, db: AsyncSession = Depends(get_db)):
    try:
        logger.debug(f"delete_user_context and user_context_id {user_context_id}")
        user_context = await db.get(UserContextModel, user_context_id)

        if not user_context:
            raise HTTPException(status_code=404, detail=f"User context with id {user_context_id} not found")

        await db.delete(user_context)
        await db.commit()

        return {"status": "User context deleted successfully"}

    except Exception as e:
        logger.error(f"Error occurred while deleting user context: {str(e)}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred")
