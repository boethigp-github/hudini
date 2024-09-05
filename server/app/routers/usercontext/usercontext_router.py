import logging
import json
from typing import List, Union
from uuid import UUID, uuid4
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from server.app.models.usercontext.user_context import UserContextModel
from server.app.models.usercontext.usercontext_post_request import UserContextPostRequestModel
from server.app.models.usercontext.usercontext_response import UserContextResponseModel, ContextDataItem
from server.app.db.base import async_session_maker

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

router = APIRouter()


async def get_db():
    async with async_session_maker() as session:
        yield session


def serialize(context_data: List[ContextDataItem]) -> str:
    return json.dumps([item.model_dump() for item in context_data])


def deserialize(context_data: Union[str, List]) -> List[ContextDataItem]:
    if isinstance(context_data, str):
        data = json.loads(context_data)
    else:
        data = context_data

    result = []
    for item in data:
        if isinstance(item, dict) and 'id' not in item:
            item['id'] = str(uuid4())
        result.append(ContextDataItem(**item))
    return result


@router.get("/usercontext", tags=["usercontext"], response_model=UserContextResponseModel)
async def get_user_contexts(user: int, thread_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(UserContextModel).where(
            UserContextModel.user == user,
            UserContextModel.thread_id == thread_id
        )
    )
    user_context = result.scalars().first()

    if not user_context:
        raise HTTPException(status_code=404, detail="No context found for the given user and thread_id")

    context_dict = user_context.to_dict()
    context_dict['context_data'] = deserialize(context_dict['context_data'])
    return UserContextResponseModel.model_validate(context_dict)


@router.post("/usercontext", tags=["usercontext"], response_model=UserContextResponseModel)
async def save_user_context(user_context: UserContextPostRequestModel, db: AsyncSession = Depends(get_db)):
    logger.debug(f"Received request to save user context: {user_context.model_dump()}")

    serialized_context_data = serialize(user_context.context_data)

    result = await db.execute(
        select(UserContextModel).where(
            UserContextModel.user == user_context.user,
            UserContextModel.thread_id == user_context.thread_id
        )
    )
    existing_user_context = result.scalars().first()

    if existing_user_context:
        logger.info(
            f"Updating existing user context with user {user_context.user} and thread_id {user_context.thread_id}")
        existing_user_context.context_data = serialized_context_data
        await db.commit()
        await db.refresh(existing_user_context)
        context_dict = existing_user_context.to_dict()
        context_dict['context_data'] = deserialize(context_dict['context_data'])
        return UserContextResponseModel.model_validate(context_dict)
    else:
        logger.info(f"Creating new user context with user {user_context.user} and thread_id {user_context.thread_id}")
        new_user_context = UserContextModel(
            user=user_context.user,
            thread_id=user_context.thread_id,
            context_data=serialized_context_data
        )
        db.add(new_user_context)
        await db.commit()
        await db.refresh(new_user_context)
        context_dict = new_user_context.to_dict()
        context_dict['context_data'] = deserialize(context_dict['context_data'])
        return UserContextResponseModel.model_validate(context_dict)


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