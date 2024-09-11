import pytest
import requests
import json
from server.app.config.settings import Settings


@pytest.fixture(scope='module')
def settings():
    # Initialize the settings and return it for reuse in the tests
    return Settings()


@pytest.fixture(scope='module')
def base_url(settings):
    # Return the BASE_URL from the settings
    return settings.get("default").get("SERVER_URL")


@pytest.fixture
def telegram_publish_payload():
    """
    Returns a valid payload for publishing a message to an authorized Telegram group using group ID.
    This payload includes the 2FA password.
    """
    return {
        "user": "JohnDoe",
        "api_id": 23915104,  # Match your TELEGRAM_CONFIG API ID
        "group_id": "@hudinitests",  # Use the group ID directly
        "message": "Test message from pytest"
    }


@pytest.fixture
def telegram_publish_payload_with_2fa(telegram_publish_payload):
    """
    Returns a valid payload for publishing a message to an authorized Telegram group with 2FA.
    This payload includes the 2FA password.
    """
    telegram_publish_payload["password"] = "8300"  # Assuming this is your 2FA password
    return telegram_publish_payload


def test_publish_with_2fa(base_url, telegram_publish_payload_with_2fa):
    """
    Test sending a message to an authorized Telegram group with 2FA enabled.
    """
    response = requests.post(f"{base_url}/socialmedia/telegram/message/send", json=telegram_publish_payload_with_2fa)

    assert response.status_code == 201
    data = response.json()
    assert "status" in data
    assert data["status"] == "Message sent successfully"
    assert "message_id" in data
