import os
import logging
from fastapi import HTTPException, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from server.app.models.gripsbox.gripsbox_model import Gripsbox
from server.app.models.gripsbox.gripsbox_post_request import GripsboxPostRequestModel
from server.app.config.settings import Settings
from server.app.models.users.user import User
from datetime import datetime
from typing import List
from server.app.db.get_db import get_db
from server.app.models.generation.success_generation_model import Message  # Ensure this is correctly imported

settings = Settings()
logger = logging.getLogger(__name__)

ALLOWED_FILE_EXTENSIONS = settings.get("default").get("ALLOWED_FILE_EXTENSIONS")

async def delete_user_gripsbox_folder(user_uuid):
    """Delete the user's gripsbox folder using the helper function."""
    gripsbox_folder = get_users_gripsbox_folder(user_uuid)

    if os.path.exists(gripsbox_folder):
        for file_name in os.listdir(gripsbox_folder):
            file_path = os.path.join(gripsbox_folder, file_name)
            if os.path.isfile(file_path):
                os.remove(file_path)
        os.rmdir(gripsbox_folder)


def get_users_gripsbox_folder(user_uuid: str) -> str:
    """Get the folder path for the user's gripsbox files."""
    storage_path = settings.get("default").get("APP_STORAGE")
    return os.path.join(storage_path, "gripsbox", user_uuid)


async def create_gripsbox_service(
    file: UploadFile,
    gripsbox_post_data: GripsboxPostRequestModel,
    user: User
) -> Gripsbox:
    # Validate file extension
    file_extension = os.path.splitext(file.filename)[1].lower()
    if file_extension not in ALLOWED_FILE_EXTENSIONS:
        logger.error(f"File type '{file_extension}' is not allowed")
        raise HTTPException(status_code=400, detail=f"File type '{file_extension}' is not allowed")

    # Use the extracted function to get the folder path
    user_gripsbox_path = get_users_gripsbox_folder(str(user.uuid))

    # Create the directory if it doesn't exist
    os.makedirs(user_gripsbox_path, exist_ok=True)

    # Check if file already exists and generate a timestamped version if necessary
    file_path = os.path.join(user_gripsbox_path, file.filename)
    if os.path.exists(file_path):
        timestamp = int(datetime.utcnow().timestamp())
        file_name, file_ext = os.path.splitext(file.filename)
        file_path = os.path.join(user_gripsbox_path, f"{file_name}_{timestamp}{file_ext}")

    # Save the file to the path
    with open(file_path, "wb") as f:
        f.write(await file.read())

    # Use get_db to get a session manually
    async for db in get_db():
        try:
            # Create a new Gripsbox entry in the database
            new_gripsbox = Gripsbox(
                user=user.uuid,
                name=gripsbox_post_data.name,
                size=gripsbox_post_data.size,
                type=gripsbox_post_data.type,
                active=gripsbox_post_data.active,
                tags=gripsbox_post_data.tags,
                models=gripsbox_post_data.models
            )

            db.add(new_gripsbox)
            await db.commit()
            await db.refresh(new_gripsbox)

            return new_gripsbox

        except Exception as e:
            await db.rollback()
            logger.error(f"Error creating gripsbox: {str(e)}")
            raise HTTPException(status_code=500, detail="Failed to create Gripsbox")


async def load_active_gripsbox_files(user_uuid: str) -> List[str]:
    """Load the contents of all active files in the user's Gripsbox."""
    user_gripsbox_path = get_users_gripsbox_folder(user_uuid)

    # Check if the Gripsbox folder exists
    if not os.path.exists(user_gripsbox_path):
        logger.error(f"Gripsbox folder for user {user_uuid} does not exist.")
        raise HTTPException(status_code=404, detail="Gripsbox folder not found.")

    # Manually use get_db() for the session
    async for db in get_db():
        result = await db.execute(
            select(Gripsbox).where(Gripsbox.user == user_uuid, Gripsbox.active == True)
        )
        active_gripsboxes = result.scalars().all()

        if not active_gripsboxes:
            logger.warning(f"No active Gripsbox files found for user {user_uuid}.")
            raise HTTPException(status_code=404, detail=f"No active Gripsbox files found for user {user_uuid}")

        # Load content from all active files
        file_contents = []
        for gripsbox_entry in active_gripsboxes:
            file_path = os.path.join(user_gripsbox_path, gripsbox_entry.name)

            # Ensure the file exists before reading it
            if os.path.exists(file_path) and os.path.isfile(file_path):
                with open(file_path, "r", encoding="utf-8") as file:
                    content = file.read()
                    file_contents.append(content)
            else:
                logger.error(f"File {gripsbox_entry.name} not found for user {user_uuid}.")
                raise HTTPException(status_code=404, detail=f"File {gripsbox_entry.name} not found.")

        return file_contents


async def add_gripsbox_content_to_llm_context(user: User) -> List[Message]:
    """Load the active Gripsbox file contents and add them to the LLM context."""
    try:
        logger.info(f"Loading active Gripsbox files for user {user.uuid}.")

        # Load the content of active Gripsbox files
        active_files_content = await load_active_gripsbox_files(user_uuid=str(user.uuid))

        # Create LLM context messages for each file
        llm_context = [
            Message(
                role="system",  # Treat as system message
                content=f"Content from Gripsbox file: {content}"
            ) for content in active_files_content
        ]

        logger.info(f"Added {len(llm_context)} Gripsbox files to LLM context for user {user.uuid}.")
        return llm_context

    except Exception as e:
        logger.error(f"Error while adding Gripsbox content to LLM context: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to add Gripsbox content to for user: {user.uuid} LLM context.")
