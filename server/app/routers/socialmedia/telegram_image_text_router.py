import logging
import json
import os
import aiohttp
import tempfile
import shutil
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from telethon import TelegramClient
from telethon.errors import SessionPasswordNeededError
from urllib.parse import urlparse
import random
import string

from server.app.config.settings import Settings

settings = Settings()

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

router = APIRouter()

# Model for request body
class PublishRequestModel(BaseModel):
    user: str
    api_id: str
    group_id: str
    caption: str
    url: str

# Model for response
class TelegramImagePublishResponseModel(BaseModel):
    status: str
    message_id: int

@router.post("/socialmedia/telegram/image/send", response_model=TelegramImagePublishResponseModel,
             status_code=status.HTTP_201_CREATED, tags=["socialmedia"])
async def publish_image_to_telegram(
        publish_request: PublishRequestModel
):
    """
    Publish an image with a caption to a specified Telegram group using a userbot.

    Args:
        publish_request: JSON body containing user, api_id, group_id, caption, and url.

    Returns:
        TelegramImagePublishResponseModel: Status and message ID of the sent message.
    """
    client = None
    temp_dir = None

    try:
        # Convert the request body to a dictionary
        publish_request_dict = publish_request.dict()
        logger.debug(f"Received publish_request: {publish_request_dict}")

        # Fetch the image from the URL
        image_url = publish_request_dict['url']
        file_extension = os.path.splitext(urlparse(image_url).path)[1] or '.png'  # Default to .png if no extension

        # Create a temporary directory and file
        temp_dir = tempfile.mkdtemp()
        temp_file_name = ''.join(random.choices(string.ascii_letters + string.digits, k=10)) + file_extension
        temp_file_path = os.path.join(temp_dir, temp_file_name)

        # Download and save the image
        async with aiohttp.ClientSession() as session:
            async with session.get(image_url) as response:
                if response.status != 200:
                    raise HTTPException(status_code=400, detail=f"Failed to download image from URL: {image_url}")
                with open(temp_file_path, "wb") as f:
                    f.write(await response.read())

        logger.debug(f"Downloaded image saved to {temp_file_path}")

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

        # Send the file with the caption
        message = await client.send_message(
            channel,
            publish_request_dict['caption'],
            file=temp_file_path
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
