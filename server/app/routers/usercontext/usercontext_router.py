import logging
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from server.app.models.usercontext.user_context import UserContextModel
from server.app.models.usercontext.usercontext_post_request_model import UserContextPostRequestModel
from server.app.models.usercontext.usercontext_post_response_model import UserContextResponseModel
from server.app.db.base import async_session_maker
from fastapi.encoders import jsonable_encoder
from pydantic import ValidationError

logger = logging.getLogger(__name__)
router = APIRouter()


async def get_db():
    async with async_session_maker() as session:
        yield session


@router.post("/usercontext", tags=["usercontext"], response_model=UserContextResponseModel)
async def save_user_context(user_context: UserContextPostRequestModel, db: AsyncSession = Depends(get_db)):
    try:
        logger.debug(f"Received request to save user context: {user_context}")

        # Serialize with jsonable_encoder to handle complex data types like UUID
        serialized_context_data = jsonable_encoder(user_context.dict())

        # Create a new UserContextModel and add it to the database
        new_user_context = UserContextModel(
            uuid=user_context.uuid,
            user=user_context.user,
            thread_id=user_context.thread_id,
            context_data=serialized_context_data  # Serialized with jsonable_encoder
        )
        db.add(new_user_context)
        await db.commit()
        await db.refresh(new_user_context)

        # Return the response
        return UserContextResponseModel(**new_user_context.to_dict())

    except ValidationError as e:
        logger.error(f"Validation error: {e.errors()}")
        raise HTTPException(status_code=422, detail={"errors": e.errors(), "message": "Validation failed"})


@router.get("/usercontext", tags=["usercontext"], response_model=UserContextResponseModel)
async def get_user_contexts(user: str, thread_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(UserContextModel)
        .where(
            UserContextModel.user == user,
            UserContextModel.thread_id == thread_id
        )
        .order_by(UserContextModel.created.desc())
    )
    user_context = result.scalars().first()

    if not user_context:
        raise HTTPException(status_code=404, detail="No context found for the given user and thread_id")

    return UserContextResponseModel(**user_context.to_dict())


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

