import logging
import json
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field
from telethon import TelegramClient
from telethon.errors import SessionPasswordNeededError
from telethon.tl.functions.messages import SendMessageRequest
from telethon.tl.types import InputPeerChat
from server.app.config.settings import Settings

settings = Settings()

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

router = APIRouter()

# Model for request
class TelegramPublishRequestModel(BaseModel):
    user: str = Field(..., description="User sending the message")
    api_id: int = Field(..., description="API ID for the Telegram account")
    group_id: str = Field(..., description="Telegram Group Name")  # Now a string for group name
    message: str = Field(..., description="Message to send")



# Model for response
class TelegramPublishResponseModel(BaseModel):
    status: str
    message_id: int


@router.post("/socialmedia/publish/telegram", response_model=TelegramPublishResponseModel,
             status_code=status.HTTP_201_CREATED, tags=["socialmedia"])
async def publish_to_telegram(publish_request: TelegramPublishRequestModel):
    """
    Publish a message to a specified Telegram group using a userbot.

    Args:
        publish_request: TelegramPublishRequestModel containing user, api_id, group_id, and message.

    Returns:
        TelegramPublishResponseModel: Status and message ID of the sent message.
    """
    client = None  # Initialize client to ensure it's available in the finally block
    logger.debug(f"Anfrage erhalten: {publish_request}")
    try:
        logger.debug(f"Attempting to send message to Telegram group ID: {publish_request.group_id}")

        # Load the TELEGRAM_CONFIG from the environment and parse it as JSON
        telegram_config = json.loads(settings.get("default").get("TELEGRAM_CONFIG"))

        # Find the Telegram provider based on the api_id submitted in the request
        telegram_provider = next(
            (provider for provider in telegram_config if provider["api_id"] == str(publish_request.api_id)), None)

        if not telegram_provider:
            raise HTTPException(status_code=404,
                                detail=f"Telegram provider configuration with api_id {publish_request.api_id} not found in TELEGRAM_CONFIG")

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

        # Use group ID directly to create the InputPeerChat
        group_peer = await client.get_input_entity(publish_request.group_id)

        # Send message to the group
        result = await client(SendMessageRequest(
            peer=group_peer,  # Use the group ID as the peer
            message=publish_request.message,
            no_webpage=True  # No preview of links
        ))

        # Extract the message ID from the result
        message_id = None
        for update in result.updates:
            if hasattr(update, 'message') and hasattr(update.message, 'id'):
                message_id = update.message.id
                break

        if message_id is None:
            raise HTTPException(status_code=500, detail="Failed to retrieve message ID from Telegram response")

        # Log and return the result
        logger.info(f"Message sent to group ID {publish_request.group_id} by user {publish_request.user}")
        return TelegramPublishResponseModel(status="Message sent successfully", message_id=message_id)

    except SessionPasswordNeededError as e:
        logger.error(f"Two-factor authentication required but failed: {str(e)}")
        raise HTTPException(status_code=403, detail="Two-factor authentication required but failed.")

    except Exception as e:
        logger.error(f"Failed to send message: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to send message: {str(e)}")

    finally:
        if client:
            await client.disconnect()
