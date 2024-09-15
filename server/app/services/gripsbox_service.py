import os
import logging
from fastapi import HTTPException, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession
from server.app.models.gripsbox.gripsbox_model import Gripsbox
from server.app.models.gripsbox.gripsbox_post_request import GripsboxPostRequestModel
from server.app.config.settings import Settings
from server.app.models.users.user import User
from datetime import datetime

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

# The extracted function for creating the user folder
def get_users_gripsbox_folder(user_uuid: str) -> str:
    storage_path = settings.get("default").get("APP_STORAGE")
    return os.path.join(storage_path, "gripsbox", user_uuid)


async def create_gripsbox_service(
        file: UploadFile,
        gripsbox_post_data: GripsboxPostRequestModel,  # Use the request model here
        db: AsyncSession,
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

    # Create a new Gripsbox entry in the database
    new_gripsbox = Gripsbox(
        user=user.uuid,
        name=gripsbox_post_data.name,
        size=gripsbox_post_data.size,
        type=gripsbox_post_data.type,
        active=gripsbox_post_data.active,
        tags=gripsbox_post_data.tags  # Use the request model's tag list
    )

    # Add and commit the new gripsbox entry to the database
    db.add(new_gripsbox)
    await db.commit()
    await db.refresh(new_gripsbox)

    return new_gripsbox

