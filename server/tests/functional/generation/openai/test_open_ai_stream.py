import unittest
import requests
import uuid
import asyncio
from server.app.config.settings import Settings
from server.app.models.generation.generation_request import GenerationRequest, ModelConfig, ModelCategory, Platform
from server.tests.test_abstract import TestAbstract


class TestGenerateAndStream(TestAbstract):
    @classmethod
    def setUpClass(cls):
        """Synchronous setup, but manually run async initialization."""
        cls.settings = Settings()
        cls.SERVER_URL = cls.settings.get("default").get("SERVER_URL")
        cls.APP_DEFAULT_ADMIN_USERNAME = cls.settings.get("default").get("APP_DEFAULT_ADMIN_USERNAME")

        # Manually run async initialization using asyncio.run()
        asyncio.run(cls.async_init())

    def test_stream_success(self):
        """Test the /stream/openai endpoint for a successful streaming response with admin authorization."""
        model_config = ModelConfig(
            id='gpt-3.5-turbo',
            platform=Platform.OPENAI,
            model="gpt-3.5-turbo",
            temperature=0.7,
            max_tokens=100,
            object="chat.completion",
            category=ModelCategory.TEXT_COMPLETION,
            description="A language model for text completions"
        )

        stream_payload = GenerationRequest(
            models=[model_config],
            prompt="Write a rant in the style of Linus Torvalds about using spaces instead of tabs for indentation in code.",
            id=str(uuid.uuid4()),  # Ensure id is a string
            method_name="fetch_completion"
        ).model_dump_json()  # Serialize payload to JSON string

        try:
            # Send a POST request to the /stream/openai endpoint with admin authorization (API key in URL)
            response = requests.post(
                f"{self.SERVER_URL}/stream/openai?api_key={self.api_key}",  # Pass api_key as query parameter
                data=stream_payload,
                headers={"Content-Type": "application/json"},
                stream=True,
                timeout=10
            )
            self.assertEqual(response.status_code, 200)  # Expect 200 OK
            self.assertEqual(response.headers['Content-Type'], 'application/json')

        except requests.RequestException as e:
            self.fail(f"Request failed: {str(e)}")


if __name__ == '__main__':
    unittest.main()
