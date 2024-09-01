import unittest
import requests
import json
import random
from pydantic import ValidationError
from server.app.config.settings import Settings
from server.app.models.generation.generation_request import GenerationRequest, ModelConfig, ModelCategory, Platform
from server.app.models.generation.success_generation_model import SuccessGenerationModel

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
            id="gpt-3.5-turbo",
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
            id=str(random.randint(1, 1000000)),  # Ensure id is a string
            prompt_id=random.randint(1, 1000000),  # Integer for prompt_id
            method_name="fetch_completion"
        ).json()  # Serialize payload to JSON

        try:
            response = requests.post(f"{self.SERVER_URL}/stream", json=json.loads(stream_payload), headers={"Content-Type": "application/json"}, stream=True, timeout=10)
            self.assertEqual(response.status_code, 200)  # Expect 200 OK
            self.assertEqual(response.headers['Content-Type'], 'application/json')

            buffer = ""
            for i, line in enumerate(response.iter_lines()):
                if line:
                    buffer += line.decode('utf-8')
                    try:
                        event_data = json.loads(buffer)
                        # Ensure all fields are present and correctly formatted
                        if 'id' not in event_data or not isinstance(event_data['id'], str):
                            self.fail("Response missing 'id' or 'id' is not a string")
                        if 'prompt_id' not in event_data:
                            self.fail("Response missing 'prompt_id'")
                        SuccessGenerationModel.parse_obj(event_data)  # Validate response model
                        buffer = ""
                    except json.JSONDecodeError:
                        continue
                    except ValidationError as e:
                        self.fail(f"Response validation error: {str(e)}")

                if i >= 50:  # Limit number of lines received
                    break
        except requests.RequestException as e:
            self.fail(f"Request failed: {str(e)}")

    def test_stream_bad_request(self):
        """Test the /stream endpoint for a bad request."""
        stream_payload = {
            "prompt": "Tell me a short joke",
            "id": str(random.randint(1, 1000000)),  # Ensure id is a string
            "prompt_id": random.randint(1, 1000000),  # Integer for prompt_id
            "method_name": "fetch_completion"
        }

        try:
            response = requests.post(f"{self.SERVER_URL}/stream", json=stream_payload)
            self.assertEqual(response.status_code, 422)
        except requests.RequestException as e:
            self.fail(f"Request failed: {str(e)}")

    def test_stream_invalid_model(self):
        """Test the /stream endpoint with an invalid model."""
        model_config = ModelConfig(
            id="invalid-model",
            platform=Platform.OPENAI,
            model="invalid-model",
            temperature=0.7,
            max_tokens=100,
            object="model",
            category=ModelCategory.TEXT_COMPLETION,
            description="Invalid model for testing"
        )

        stream_payload = GenerationRequest(
            models=[model_config],
            prompt="Tell me a short joke",
            id=str(random.randint(1, 1000000)),  # Ensure id is a string
            prompt_id=random.randint(1, 1000000),  # Integer for prompt_id
            method_name="fetch_completion"
        ).json()  # Serialize payload to JSON

        try:
            response = requests.post(f"{self.SERVER_URL}/stream", json=json.loads(stream_payload), headers={"Content-Type": "application/json"})
            self.assertEqual(response.status_code, 422)  # Expect 422 Unprocessable Entity
        except requests.RequestException as e:
            self.fail(f"Request failed: {str(e)}")

    def test_stream_unsupported_platform(self):
        """Test the /stream endpoint with an unsupported platform."""
        model_config = ModelConfig(
            id="some-model",
            platform="unsupported_platform",
            model="some-model",
            temperature=0.7,
            max_tokens=100,
            object="model",
            category=ModelCategory.TEXT_COMPLETION,
            description="Model on unsupported platform"
        )

        stream_payload = GenerationRequest(
            models=[model_config],
            prompt="This is a test",
            id=str(random.randint(1, 1000000)),  # Ensure id is a string
            prompt_id=random.randint(1, 1000000),  # Integer for prompt_id
            method_name="fetch_completion"
        ).json()  # Serialize payload to JSON

        try:
            response = requests.post(f"{self.SERVER_URL}/stream", json=json.loads(stream_payload), headers={"Content-Type": "application/json"})
            self.assertEqual(response.status_code, 422)  # Expect 422 Unprocessable Entity
        except requests.RequestException as e:
            self.fail(f"Request failed: {str(e)}")

if __name__ == '__main__':
    unittest.main()
