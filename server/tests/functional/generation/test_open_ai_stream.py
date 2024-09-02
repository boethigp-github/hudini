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
        """Test the /stream endpoint for a successful streaming response."""
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
                f"{self.SERVER_URL}/stream",
                data=stream_payload,  # Pass the JSON string
                headers={"Content-Type": "application/json"},
                stream=True,
                timeout=10
            )
            self.assertEqual(response.status_code, 200)  # Expect 200 OK
            self.assertEqual(response.headers['Content-Type'], 'application/json')


        except requests.RequestException as e:
            self.fail(f"Request failed: {str(e)}")

    def test_stream_bad_request(self):
        """Test the /stream endpoint for a bad request."""
        # Manually create a malformed request payload
        malformed_payload = {
            "prompt": "Tell me a short joke",
            "id": str(random.randint(1, 1000000)),
            "prompt_id": random.randint(1, 1000000),
            "method_name": "fetch_completion"
            # Missing required field 'models'
        }
        malformed_payload_json = json.dumps(malformed_payload)  # Convert to JSON string

        try:
            response = requests.post(
                f"{self.SERVER_URL}/stream",
                data=malformed_payload_json,  # Pass the JSON string
                headers={"Content-Type": "application/json"}
            )
            self.assertEqual(response.status_code, 422)  # Expect 422 Unprocessable Entity
        except requests.RequestException as e:
            self.fail(f"Request failed: {str(e)}")



    # def test_stream_unsupported_platform(self):
    #     """Test the /stream endpoint with an unsupported platform."""
    #     unsupported_platform_payload = {
    #         "models": [{
    #             "id": "some-model",
    #             "platform": "unsupported_platform",  # Using an invalid platform
    #             "model": "some-model",
    #             "temperature": 0.7,
    #             "max_tokens": 100,
    #             "object": "model",
    #             "category": "text_completion",
    #             "description": "Model on unsupported platform"
    #         }],
    #         "prompt": "This is a test",
    #         "id": str(random.randint(1, 1000000)),
    #         "prompt_id": random.randint(1, 1000000),
    #         "method_name": "fetch_completion"
    #     }
    #     unsupported_platform_payload_json = json.dumps(unsupported_platform_payload)  # Convert to JSON string
    #
    #     try:
    #         response = requests.post(
    #             f"{self.SERVER_URL}/stream",
    #             data=unsupported_platform_payload_json,  # Pass the JSON string
    #             headers={"Content-Type": "application/json"}
    #         )
    #         self.assertEqual(response.status_code, 422)  # Expect 422 Unprocessable Entity
    #     except requests.RequestException as e:
    #         self.fail(f"Request failed: {str(e)}")

if __name__ == '__main__':
    unittest.main()
