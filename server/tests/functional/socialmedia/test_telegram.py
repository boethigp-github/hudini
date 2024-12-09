import pytest
import requests
from server.app.config.settings import Settings
from server.tests.test_abstract import TestAbstract  # Assuming this contains API key logic
import asyncio


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
        "api_id": 23915104,  # Match your SOCIALMEDIA_USER API ID
        "group_id": "@hudinitest",  # Use the group ID directly
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


class TestTelegramPublish(TestAbstract):
    @classmethod
    def setUpClass(cls):
        """
        Synchronous setup, including the API key retrieval.
        This method runs async initialization from the base class (TestAbstract).
        """
        cls.settings = Settings()
        cls.BASE_URL = cls.settings.get("default").get("SERVER_URL")
        cls.APP_DEFAULT_ADMIN_USERNAME = cls.settings.get("default").get("APP_DEFAULT_ADMIN_USERNAME")
        # Manually run async initialization to retrieve the API key
        asyncio.run(cls.async_init())

    def test_publish_with_2fa(self):
        """
        Test sending a message to an authorized Telegram group with 2FA enabled.
        This uses the API key from the abstract test class.
        """
        # Manually inject the base_url and telegram_publish_payload_with_2fa fixtures
        base_url = self.BASE_URL
        telegram_publish_payload_with_2fa = {
            "user": "JohnDoe",
            "api_id": 23915104,  # Match your SOCIALMEDIA_USER API ID
            "group_id": "@hudinitest",  # Use the group ID directly
            "message": "Test message from pytest",
            "password": "8300"  # Assuming this is your 2FA password
        }

        # Use the API key from the TestAbstract class
        response = requests.post(
            f"{base_url}/socialmedia/telegram/message/send?api_key={self.api_key}",
            json=telegram_publish_payload_with_2fa
        )

        # Asserting the response status and structure
        assert response.status_code == 201, f"Unexpected status code: {response.status_code}"
        data = response.json()
        assert "status" in data, "Response is missing 'status' field"
        assert data["status"] == "Message sent successfully", f"Unexpected status: {data['status']}"
        assert "message_id" in data, "Response is missing 'message_id'"

    def test_publish_without_2fa(self):
        """
        Test sending a message to an authorized Telegram group without 2FA enabled.
        """
        # Manually inject the base_url and telegram_publish_payload fixtures
        base_url = self.BASE_URL
        telegram_publish_payload = {
            "user": "JohnDoe",
            "api_id": 23915104,  # Match your SOCIALMEDIA_USER API ID
            "group_id": "@hudinitest",  # Use the group ID directly
            "message": "Test message from pytest"
        }

        # Use the API key from the TestAbstract class
        response = requests.post(
            f"{base_url}/socialmedia/telegram/message/send?api_key={self.api_key}",
            json=telegram_publish_payload
        )

        # Asserting the response status and structure
        assert response.status_code == 201, f"Unexpected status code: {response.status_code}"
        data = response.json()
        assert "status" in data, "Response is missing 'status' field"
        assert data["status"] == "Message sent successfully", f"Unexpected status: {data['status']}"
        assert "message_id" in data, "Response is missing 'message_id'"
