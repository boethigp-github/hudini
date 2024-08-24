import unittest
import requests
import json
import time

class TestGenerateAndStream(unittest.TestCase):

    from server.app.config.base_config import BaseConfig
    SERVER_URL = BaseConfig.SERVER_URL

    def test_stream_success(self):
        """Test the /stream endpoint for a successful streaming response."""
        stream_payload = {
            "prompt": "Tell me a short joke",
            "models": ["gpt-3.5-turbo"]  # Adjust to a valid model list
        }
        response = requests.post(f"{self.SERVER_URL}/stream", json=stream_payload, stream=True, timeout=10)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers['Content-Type'], 'application/json')

        # Handle streaming responses
        buffer = ""
        timeout_seconds = 10  # Set a timeout for the test
        start_time = time.time()

        # Iterate over the streaming response lines
        for i, line in enumerate(response.iter_lines()):
            if line:
                # Decode and process the line
                buffer += line.decode('utf-8')
                try:
                    # Try to parse the buffer as JSON
                    event_data = json.loads(buffer)
                    # Check that the expected keys are in the JSON response
                    self.assertIn("model", event_data)
                    self.assertIn("completion", event_data)
                    buffer = ""  # Reset buffer after successful parsing
                except json.JSONDecodeError:
                    # If JSON is not fully formed, continue reading more lines
                    continue

            # Timeout safeguard
            if time.time() - start_time > timeout_seconds:
                self.fail("Test timed out while waiting for stream response.")

            # Safeguard to avoid infinite loops in case of an issue
            if i >= 50:
                break

    def test_stream_bad_request(self):
        """Test the /stream endpoint for a bad request."""

        stream_payload = {
            "prompt": "Tell me a short joke"
        }
        response = requests.post(f"{self.SERVER_URL}/stream", json=stream_payload)
        self.assertEqual(response.status_code, 400)

    def test_stream_server_error(self):
        """Test the /stream endpoint for a server error."""


        stream_payload = {
            "prompt": "This is a test",
            "models": ["invalid-model"]
        }
        response = requests.post(f"{self.SERVER_URL}/stream", json=stream_payload)
        self.assertEqual(response.status_code, 200)

if __name__ == '__main__':
    unittest.main()
