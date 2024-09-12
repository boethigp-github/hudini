import logging
import json
import os
from fastapi import APIRouter, HTTPException, status, UploadFile, File, Query
from pydantic import BaseModel
from telethon import TelegramClient
from telethon.errors import SessionPasswordNeededError
import tempfile
import shutil

from server.app.config.settings import Settings

settings = Settings()

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

router = APIRouter()

# Model for response
class TelegramImagePublishResponseModel(BaseModel):
    status: str
    message_id: int

@router.post("/socialmedia/telegram/image/send", response_model=TelegramImagePublishResponseModel,
             status_code=status.HTTP_201_CREATED, tags=["socialmedia"])
async def publish_image_to_telegram(
        publish_request: str = Query(..., description="JSON string containing publish request data"),
        file: UploadFile = File(...)
):
    """
    Publish an image with a caption to a specified Telegram group using a userbot.

    Args:
        publish_request: JSON string containing user, api_id, group_id, and caption.
        file: The image file to be uploaded.

    Returns:
        TelegramImagePublishResponseModel: Status and message ID of the sent message.
    """
    client = None
    temp_dir = None

    try:
        # Parse the publish_request JSON string
        publish_request_dict = json.loads(publish_request)
        logger.debug(f"Received publish_request: {publish_request_dict}")
        logger.debug(f"Received file: {file.filename}")

        # Create a temporary directory
        temp_dir = tempfile.mkdtemp()
        temp_file_path = os.path.join(temp_dir, file.filename)

        # Save the uploaded file with its original filename
        with open(temp_file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        logger.debug(f"Attempting to send image to Telegram group ID: {publish_request_dict['group_id']}")

        # Load the TELEGRAM_CONFIG from the environment and parse it as JSON
        telegram_config = json.loads(settings.get("default").get("TELEGRAM_CONFIG"))

        # Find the Telegram provider based on the api_id submitted in the request
        telegram_provider = next(
            (provider for provider in telegram_config if provider["api_id"] == str(publish_request_dict['api_id'])),
            None)

        if not telegram_provider:
            raise HTTPException(status_code=404,
                                detail=f"Telegram provider configuration with api_id {publish_request_dict['api_id']} not found in TELEGRAM_CONFIG")

        # Telethon client (Userbot)
        api_id = telegram_provider["api_id"]
        api_hash = telegram_provider["api_hash"]
        phone_number = telegram_provider["phone_number"]
        password = telegram_provider.get("password")  # Get the 2FA password if available

        client = TelegramClient('userbot', api_id, api_hash)

        # Start client and authenticate
        await client.start(phone=phone_number)

        # Handle 2FA if required
        if not await client.is_user_authorized():
            logger.debug(f"2FA required for user {phone_number}.")
            if password:
                try:
                    await client.sign_in(password=password)
                    logger.info(f"Successfully signed in with 2FA for {phone_number}.")
                except SessionPasswordNeededError:
                    logger.error(f"2FA failed: Incorrect or missing password for {phone_number}.")
                    raise HTTPException(status_code=403, detail="Two-factor authentication failed.")
            else:
                logger.error("2FA is required, but no password was provided.")
                raise HTTPException(status_code=403, detail="Two-factor authentication is required.")
        else:
            logger.info(f"User {phone_number} is already authorized.")

        # Get the target chat
        channel = await client.get_entity(publish_request_dict['group_id'])

        # Send the file with the original filename
        message = await client.send_file(
            channel,
            temp_file_path,
            caption=publish_request_dict['caption'],
            file_name=file.filename  # Use the original filename
        )

        # Log and return the result
        logger.info(f"Image sent to group ID {publish_request_dict['group_id']} by user {publish_request_dict['user']}")
        return TelegramImagePublishResponseModel(status="Image sent successfully", message_id=message.id)

    except json.JSONDecodeError:
        logger.error("Failed to parse publish_request JSON")
        raise HTTPException(status_code=400, detail="Invalid JSON in publish_request")

    except SessionPasswordNeededError as e:
        logger.error(f"Two-factor authentication required but failed: {str(e)}")
        raise HTTPException(status_code=403, detail="Two-factor authentication required but failed.")

    except Exception as e:
        logger.error(f"Failed to send image: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to send image: {str(e)}")

    finally:
        if client:
            await client.disconnect()
        if temp_dir:
            shutil.rmtree(temp_dir)