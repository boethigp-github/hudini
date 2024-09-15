import os
import logging
from fastapi import HTTPException, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession
from server.app.models.gripsbox.gripsbox_model import Gripsbox
from server.app.models.gripsbox.gripsbox_post_request import GripsboxPostRequestModel
from server.app.config.settings import Settings
from server.app.models.users.user import User
settings = Settings()
logger = logging.getLogger(__name__)

# No default fallback; assuming the settings object provides valid data
ALLOWED_FILE_EXTENSIONS = settings.get("default").get("ALLOWED_FILE_EXTENSIONS")

async def create_gripsbox_service(
    file: UploadFile,
    name: str,
    size: int,
    type: str,
    active: bool,
    tags: str,
    db: AsyncSession,
    user: User
) -> Gripsbox:
    # Log the incoming data
    logger.debug(f"Incoming file: {file.filename}")
    logger.debug(f"Incoming metadata: name={name}, size={size}, type={type}, active={active}, tags={tags}")

    # Validate file extension
    file_extension = os.path.splitext(file.filename)[1].lower()
    if file_extension not in ALLOWED_FILE_EXTENSIONS:
        logger.error(f"File type '{file_extension}' is not allowed")
        raise HTTPException(status_code=400, detail=f"File type '{file_extension}' is not allowed")

    # Convert tags from a comma-separated string to a list
    tags_list = [tag.strip() for tag in tags.split(',')]

    # Create GripsboxPostRequestModel instance
    gripsbox_data = GripsboxPostRequestModel(
        name=name,
        size=size,
        type=type,
        active=active,
        tags=tags_list
    )

    # Get storage path from settings and create a user-specific folder
    storage_path = settings.get("default").get("APP_STORAGE")
    user_gripsbox_path = os.path.join(storage_path, "gripsbox", User.uuid)

    # Create the directory if it doesn't exist
    os.makedirs(user_gripsbox_path, exist_ok=True)

    # Define the file location
    file_location = os.path.join(user_gripsbox_path, file.filename)

    # Save the file to disk
    try:
        with open(file_location, "wb") as f:
            f.write(await file.read())
    except Exception as e:
        logger.error(f"Error saving file {file.filename}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error saving file: {str(e)}")

    # Create and save new gripsbox record
    try:
        new_gripsbox = Gripsbox(
            name=gripsbox_data.name,
            size=gripsbox_data.size,
            type=gripsbox_data.type,
            active=gripsbox_data.active,
            tags=gripsbox_data.tags
        )
        db.add(new_gripsbox)
        await db.commit()
        await db.refresh(new_gripsbox)
    except Exception as e:
        logger.error(f"Error creating gripsbox record: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error creating record: {str(e)}")

    # Log the newly created gripsbox
    logger.debug(f"Gripsbox created successfully: {new_gripsbox}")

    return new_gripsbox
