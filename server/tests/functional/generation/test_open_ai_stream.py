import unittest
import requests
import json
import random
from server.app.config.settings import Settings
from server.app.models.generation.generation_request import GenerationRequest, ModelConfig, ModelCategory, Platform
from server.app.models.generation.success_generation_model import SuccessGenerationModel
import uuid
class TestGenerateAndStream(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # Initialize settings
        cls.settings = Settings()
        # Set SERVER_URL from loaded configuration
        cls.SERVER_URL = cls.settings.get("default").get("SERVER_URL")

    def test_stream_success(self):
        """Test the /stream/openai endpoint for a successful streaming response."""
        model_config = ModelConfig(
            id=str(uuid.uuid4()),
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
            response = requests.post(
                f"{self.SERVER_URL}/stream/openai",
                data=stream_payload,  # Pass the JSON string
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
