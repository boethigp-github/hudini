import unittest
import requests
import os
from dotenv import load_dotenv
import json

from jsonschema import validate
import time

# Get the current file's directory
current_dir = os.path.dirname(os.path.abspath(__file__))

# Construct the path to .env.local
env_path = os.path.join(current_dir, '..', '..', '.env.local')

# Load environment variables from .env.local
load_dotenv(env_path)



class TestGenerateAndStream(unittest.TestCase):
    BASE_URL = os.getenv('SERVER_URL', 'http://localhost:5000')

    def test_generate(self):
        payload = {
            "prompt": "What is the capital of France?",
            "models": ["gpt-3.5-turbo"]  # Adjust this to a list of models you know exists
        }
        response = requests.post(f"{self.BASE_URL}/generate", json=payload)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('status', data)
        self.assertEqual(data['status'], "Prompt and models received")
        self.assertIn('prompt_id', data)  # Check if 'prompt_id' is included in the response

    def test_stream(self):
        # First, send a generate request
        generate_payload = {
            "prompt": "Tell me a short joke",
            "models": ["gpt-3.5-turbo"]  # Adjust this to a list of models you know exists
        }
        generate_response = requests.post(f"{self.BASE_URL}/generate", json=generate_payload)
        self.assertEqual(generate_response.status_code, 200)
        generate_data = generate_response.json()
        self.assertIn('prompt_id', generate_data)  # Ensure 'prompt_id' is present

        # Then, test the stream endpoint
        stream_payload = {
            "prompt": "Tell me a short joke",
            "models": ["gpt-3.5-turbo"],  # Adjust this to a list of models you know exists
            "prompt_id": generate_data['prompt_id'],  # Use the prompt_id from the generate request
            "user": "test_user"  # Optional: specify a user if required by your app
        }
        response = requests.post(f"{self.BASE_URL}/stream", json=stream_payload, stream=True, timeout=10)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers['Content-Type'], 'application/json')

        # Handle streaming responses
        buffer = ""
        timeout_seconds = 10  # Set a timeout for the test
        start_time = time.time()

        for i, line in enumerate(response.iter_lines()):
            if line:
                # Decode the line and append it to the buffer
                buffer += line.decode('utf-8')
                try:
                    # Try to parse the buffer as JSON
                    event_data = json.loads(buffer)
                    # Validate the event data against the StreamResponse schema
                    from server.app.utils.swagger_loader import SwaggerLoader
                    swagger_loader = SwaggerLoader("swagger.yaml")
                    stream_response_schema = swagger_loader.get_component_schema("StreamResponse")
                    validate(instance=event_data, schema=stream_response_schema)
                    # Reset buffer after successful parsing
                    buffer = ""
                except json.JSONDecodeError:
                    # If JSON is not fully formed, continue reading more lines
                    continue
                except Exception as e:
                    self.fail(f"Schema validation failed: {str(e)}")
            if time.time() - start_time > timeout_seconds:
                self.fail("Test timed out while waiting for stream response.")
            if i >= 50:  # Safeguard to avoid infinite loops in case of an issue
                break

if __name__ == '__main__':
    unittest.main()
