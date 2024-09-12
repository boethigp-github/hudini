import pytest
import requests
import json
import urllib.parse
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
        "api_id": 23915104,
        "group_id": "@hudinitests",
        "caption": "Test caption from pytest"
    }


def test_publish_image_with_2fa(base_url, telegram_image_publish_payload):
    """
    Test sending an image to an authorized Telegram group with 2FA enabled.
    """
    # Convert the payload to a JSON string and URL-encode it
    encoded_payload = urllib.parse.quote(json.dumps(telegram_image_publish_payload))

    # Construct the URL with the encoded payload as a query parameter
    url = f"{base_url}/socialmedia/telegram/image/send?publish_request={encoded_payload}"

    # Specify the filename
    filename = "test-image.png"

    # Open the image file in binary mode
    with open(filename, 'rb') as image_file:
        # Prepare the file data
        files = {
            'file': (filename, image_file, 'image/png')
        }

        # Send the POST request
        response = requests.post(url, files=files)

    # Print response content for debugging
    print(f"Response status code: {response.status_code}")
    print(f"Response content: {response.content}")

    # Assertions
    assert response.status_code == 201
    data = response.json()
    assert "status" in data
    assert data["status"] == "Image sent successfully"
    assert "message_id" in data


# Additional test cases

