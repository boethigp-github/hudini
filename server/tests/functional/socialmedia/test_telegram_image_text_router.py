import pytest
import requests
import json
from server.app.config.settings import Settings
from server.tests.test_abstract import TestAbstract  # Assuming this contains API key logic
import asyncio

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
        "group_id": "@hudinitest",
        "caption": "Test caption from pytest",
        "url": "https://testimages.org/img/testimages_screenshot.jpg"  # Ensure this URL points to a valid image for testing
    }

class TestTelegramPublishWithImage(TestAbstract):
    @classmethod
    def setUpClass(cls):
        """
        Synchronous setup, including the API key retrieval.
        This method runs async initialization from the base class (TestAbstract).
        """
        cls.settings = Settings()
        cls.BASE_URL = cls.settings.get("default").get("SERVER_URL")
        # Manually run async initialization to retrieve the API key
        cls.APP_DEFAULT_ADMIN_USERNAME = cls.settings.get("default").get("APP_DEFAULT_ADMIN_USERNAME")
        asyncio.run(cls.async_init())


    def test_publish_image_with_2fa(self):
        """
        Test sending an image to an authorized Telegram group with 2FA enabled.
        This uses the API key from the abstract test class.
        """
        # Construct the URL for the POST request
        url = f"{self.BASE_URL}/socialmedia/telegram/image/send?api_key={self.api_key}"

        # Send the POST request with the JSON payload
        response = requests.post(
            url,
            json={
        "user": "JohnDoe",
        "api_id": "23915104",
        "group_id": "@hudinitest",
        "caption": "Test caption from pytest",
        "url": "https://testimages.org/img/testimages_screenshot.jpg"  # Ensure this URL points to a valid image for testing
    },
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
