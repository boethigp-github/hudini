import pytest
import requests
import json
from server.app.config.settings import Settings

@pytest.fixture(scope='module')
def settings():
    return Settings()

@pytest.fixture(scope='module')
def base_url(settings):
    return settings.get("default").get("SERVER_URL")

@pytest.fixture
def telegram_image_publish_payload():
    return {
        "user": "JohnDoe",
        "api_id": "23915104",
        "group_id": "@hudinitests",
        "caption": "Test caption from pytest",
        "url": "https://testimages.org/img/testimages_screenshot.jpg"  # Ensure this URL points to a valid image for testing
    }

def test_publish_image_with_2fa(base_url, telegram_image_publish_payload):
    """
    Test sending an image to an authorized Telegram group with 2FA enabled.
    """
    # Construct the URL for the POST request
    url = f"{base_url}/socialmedia/telegram/image/send"

    # Send the POST request with the JSON payload
    response = requests.post(
        url,
        json=telegram_image_publish_payload,
        headers={"Content-Type": "application/json"}
    )

    # Print response content for debugging
    print(f"Response status code: {response.status_code}")
    print(f"Response content: {response.content}")

    # Assertions
    assert response.status_code == 201
    data = response.json()
    assert "status" in data
    assert data["status"] == "Image sent successfully"
    assert "message_id" in data
