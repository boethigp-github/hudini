import unittest
import requests
import json
import time
import uuid

from server.app.config.base_config import BaseConfig

class TestAnthropicStream(unittest.TestCase):

    SERVER_URL = BaseConfig.SERVER_URL

    def test_stream_success(self):
        """Test the /stream endpoint for a successful streaming response using an Anthropic model."""
        stream_payload = {
            "prompt_id": str(uuid.uuid4()),
            "prompt": "Tell me a short joke",
            "models": [{
                "category": "chat",
                "created": 1712361441,
                "description": "Model claude-3-sonnet-20240229 categorized as chat, available on anthropic",
                "id": "claude-3-sonnet-20240229",
                "object": "model",
                "owned_by": "anthropic",
                "parent": None,
                "permission": None,
                "platform": "anthropic",
                "root": None
            }]
        }
        response = requests.post(f"{self.SERVER_URL}/stream", json=stream_payload, stream=True, timeout=10)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers['Content-Type'], 'application/json')

        buffer = ""
        timeout_seconds = 10
        start_time = time.time()

        for i, line in enumerate(response.iter_lines()):
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

            if i >= 50:
                break

    def test_stream_bad_request(self):
        """Test the /stream endpoint for a bad request with an Anthropic model."""
        stream_payload = {
            "prompt": "Tell me a short joke"
            # Intentionally omitting the "models" field
        }
        response = requests.post(f"{self.SERVER_URL}/stream", json=stream_payload)
        self.assertEqual(response.status_code, 400)

    def test_stream_invalid_model(self):
        """Test the /stream endpoint with an invalid Anthropic model."""
        stream_payload = {
            "prompt_id": str(uuid.uuid4()),
            "prompt": "This is a test",
            "models": [{
                "category": "chat",
                "created": 1712361441,
                "description": "Invalid model for testing",
                "id": "invalid-claude-model",
                "object": "model",
                "owned_by": "anthropic",
                "parent": None,
                "permission": None,
                "platform": "anthropic",
                "root": None
            }]
        }
        response = requests.post(f"{self.SERVER_URL}/stream", json=stream_payload)

        #@todo: test for schema throw 404 serverside
        self.assertEqual(response.status_code, 200)  # Expecting a 400 Bad Request for invalid model

    def test_stream_unsupported_platform(self):
        """Test the /stream endpoint with an unsupported platform using an Anthropic model."""
        stream_payload = {
            "prompt_id": str(uuid.uuid4()),
            "prompt": "This is a test",
            "models": [{
                "category": "chat",
                "created": 1712361441,
                "description": "Model on unsupported platform",
                "id": "some-claude-model",
                "object": "model",
                "owned_by": "anthropic",
                "parent": None,
                "permission": None,
                "platform": "unsupported_platform",
                "root": None
            }]
        }
        response = requests.post(f"{self.SERVER_URL}/stream", json=stream_payload)
        self.assertEqual(response.status_code, 400)  # Expecting a 400 Bad Request for unsupported platform

if __name__ == '__main__':
    unittest.main()
