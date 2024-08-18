import unittest
import requests
import os
from dotenv import load_dotenv
import json

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
        response = requests.post(f"{self.BASE_URL}/stream", json=stream_payload, stream=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers['Content-Type'], 'application/json')

        # Define expected properties based on the StreamResponse schema
        expected_properties = ["status", "model", "token", "timestamp", "user", "prompt", "prompt_id"]

        # Handle streaming responses
        buffer = ""
        for i, line in enumerate(response.iter_lines()):
            if line:
                # Decode the line and append it to the buffer
                buffer += line.decode('utf-8')
                try:
                    # Try to parse the buffer as JSON
                    event_data = json.loads(buffer)
                    # Check if all expected properties exist in the event data
                    for prop in expected_properties:
                        self.assertIn(prop, event_data, f"Property '{prop}' is missing from the event data")
                    # Reset buffer after successful parsing
                    buffer = ""
                except json.JSONDecodeError:
                    # If JSON is not fully formed, continue reading more lines
                    continue
            if i >= 50:  # Safeguard to avoid infinite loops in case of an issue
                break

if __name__ == '__main__':
    unittest.main()
