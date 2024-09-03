import unittest
import requests
import json
import random
import time
from server.app.config.settings import Settings
import uuid
from requests.exceptions import ChunkedEncodingError

class TestAnthropicStream(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # Initialize the settings
        cls.settings = Settings()

        # Set the SERVER_URL from the loaded configuration
        cls.SERVER_URL = cls.settings.get("default").get("SERVER_URL")

    def test_stream_success(self):
        """Test the /stream/anthropic endpoint for a successful streaming response using an Anthropic model."""
        stream_payload = {
            "id": str(uuid.uuid4()),  # Ensure id is a string
            "prompt": "Tell me a short joke",
            "models": [{
                "category": "text_completion",  # Ensure valid category
                "created": 1712361441,
                "description": "Model claude-3-sonnet-20240229 categorized as text_completion, available on anthropic",
                "id": str(uuid.uuid4()),
                "model": "claude-3-sonnet-20240229",
                "object": "model",
                "owned_by": "anthropic",
                "parent": None,
                "permission": None,
                "platform": "anthropic",
                "root": None
            }]
        }
        response = requests.post(f"{self.SERVER_URL}/stream/anthropic", json=stream_payload, stream=True, timeout=20)  # Increased timeout
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers['Content-Type'], 'application/json')

        buffer = ""
        timeout_seconds = 20  # Increased timeout for streaming
        start_time = time.time()

        for line in response.iter_lines():
            if line:
                buffer += line.decode('utf-8')
                try:
                    event_data = json.loads(buffer)
                    self.assertIn("model", event_data)
                    self.assertIn("completion", event_data)
                    buffer = ""
                except json.JSONDecodeError:
                    continue

            if time.time() - start_time > timeout_seconds:
                self.fail("Test timed out while waiting for stream response.")


        self.assertEqual(response.status_code, 200)

    def test_stream_invalid_model(self):
        """Test the /stream/anthropic endpoint with an invalid Anthropic model."""
        stream_payload = {
            "id": str(random.randint(1, 1000000)),  # Ensure id is a string
            "prompt": "This is a test",
            "models": [{
                "category": "text_completion",  # Ensure valid category
                "created": 1712361441,
                "description": "Invalid model for testing",
                "id": "invalid-claude-model",
                "model": "invalid-claude-model",
                "object": "model",
                "owned_by": "anthropic",
                "parent": None,
                "permission": None,
                "platform": "anthropic",
                "root": None
            }]
        }
        response = requests.post(f"{self.SERVER_URL}/stream/anthropic", json=stream_payload, stream=True)
        self.assertEqual(response.status_code, 200)

if __name__ == '__main__':
    unittest.main()
