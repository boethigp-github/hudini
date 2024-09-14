import logging
from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from server.app.models.usercontext.user_context import UserContextModel
from server.app.models.usercontext.usercontext_post_request_model import UserContextPostRequestModel
from server.app.models.usercontext.usercontext_post_response_model import UserContextResponseModel
from server.app.db.base import async_session_maker
from fastapi.encoders import jsonable_encoder
from datetime import datetime
from typing import List
import openpyxl
from io import BytesIO
from fastapi.responses import StreamingResponse
from server.app.utils.check_user_session import check_user_session
logger = logging.getLogger(__name__)
router = APIRouter()


# Dependency to get database session
async def get_db():
    async with async_session_maker() as session:
        yield session


from pydantic import ValidationError


# Route to save user context
@router.post("/usercontext", tags=["usercontext"], response_model=List[UserContextResponseModel])
async def save_user_context(
        user_contexts: List[UserContextPostRequestModel],
        db: AsyncSession = Depends(get_db),
        access_token: str = Depends(check_user_session)  # Session check dependency
):
    try:
        logger.debug(f"Received request to save user contexts from user with access_token: {access_token}")

        saved_contexts = []
        for user_context in user_contexts:
            if not user_context.prompt.context_data:
                raise HTTPException(status_code=400, detail="Context data must not be empty")

            existing_context = await db.get(UserContextModel, user_context.uuid)
            if existing_context:
                existing_context.user = user_context.user
                existing_context.thread_id = user_context.thread_id
                existing_context.context_data = jsonable_encoder(user_context.dict())
                existing_context.updated = datetime.now()
                new_user_context = existing_context
            else:
                new_user_context = UserContextModel(
                    uuid=user_context.uuid,
                    user=user_context.user,
                    thread_id=user_context.thread_id,
                    context_data=jsonable_encoder(user_context.dict()),
                    updated=datetime.now()
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
    except Exception as e:
        logger.error(f"Error saving user context: {str(e)}")
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")


# Route to get user context
@router.get("/usercontext", tags=["usercontext"], response_model=List[UserContextResponseModel])
async def get_user_contexts(
        user: str,
        thread_id: int,
        db: AsyncSession = Depends(get_db),
        access_token: str = Depends(check_user_session)  # Session check dependency
):
    logger.debug(f"Fetching contexts for user {user} with access_token: {access_token}")

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


# Route to delete user context
@router.delete("/usercontext/{thread_id}", tags=["usercontext"])
async def delete_user_context(
        thread_id: int,
        db: AsyncSession = Depends(get_db),
        access_token: str = Depends(check_user_session)  # Session check dependency
):
    try:
        logger.debug(f"Deleting contexts for thread {thread_id} with access_token: {access_token}")

        result = await db.execute(
            select(UserContextModel).where(UserContextModel.thread_id == thread_id)
        )
        user_contexts = result.scalars().all()

        if not user_contexts:
            raise HTTPException(status_code=404, detail=f"No user contexts found for thread_id {thread_id}")

        for user_context in user_contexts:
            await db.delete(user_context)

        await db.commit()
        return {"status": f"All user contexts with thread_id {thread_id} deleted successfully"}

    except Exception as e:
        logger.error(f"Error occurred while deleting user contexts: {str(e)}")
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")


# Route to export user context to Excel
@router.get("/usercontext/export/excel", tags=["usercontext"])
async def export_user_context_to_excel(
        user: str = Query(..., description="UUID of the user"),
        thread_id: int = Query(..., description="ID of the thread"),
        db: AsyncSession = Depends(get_db),
        access_token: str = Depends(check_user_session)  # Session check dependency
):
    try:
        logger.debug(f"Exporting Excel for user {user} with access_token: {access_token}")

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
            logger.error(f"No contexts found for user {user} and thread_id {thread_id}")
            raise HTTPException(status_code=404, detail="No contexts found for the given user and thread_id")

        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "User Contexts"
        headers = ["UUID", "User", "Thread ID", "Context Data", "Created", "Updated"]
        ws.append(headers)

        for context in user_contexts:
            ws.append([
                str(context.uuid),
                str(context.user),
                context.thread_id,
                str(context.context_data),
                context.created.strftime("%Y-%m-%d %H:%M:%S"),
                context.updated.strftime("%Y-%m-%d %H:%M:%S") if context.updated else ""
            ])

        buffer = BytesIO()
        wb.save(buffer)
        buffer.seek(0)

        return StreamingResponse(
            buffer,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": "attachment; filename=user_context_export.xlsx"}
        )

    except Exception as e:
        logger.error(f"Error occurred during Excel export: {str(e)}")
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")
