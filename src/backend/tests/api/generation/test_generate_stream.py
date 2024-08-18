import unittest
import requests
import os
from dotenv import load_dotenv
import json
import yaml
from jsonschema import validate

# Get the current file's directory
current_dir = os.path.dirname(os.path.abspath(__file__))

# Construct the path to .env.local
env_path = os.path.join(current_dir, '..', '..', '.env.local')

# Load environment variables from .env.local
load_dotenv(env_path)

# Load the Swagger YAML file
swagger_path = os.path.join(os.path.abspath(__file__), '..', '..', '..', '..', 'swagger.yaml')
with open(swagger_path, 'r') as file:
    swagger_def = yaml.safe_load(file)

# Extract the StreamResponse schema
stream_response_schema = swagger_def['components']['schemas']['StreamResponse']

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

        # Handle streaming responses
        buffer = ""
        for i, line in enumerate(response.iter_lines()):
            if line:
                # Decode the line and append it to the buffer
                buffer += line.decode('utf-8')
                try:
                    # Try to parse the buffer as JSON
                    event_data = json.loads(buffer)
                    # Validate the event data against the StreamResponse schema
                    validate(instance=event_data, schema=stream_response_schema)
                    # Reset buffer after successful parsing
                    buffer = ""
                except json.JSONDecodeError:
                    # If JSON is not fully formed, continue reading more lines
                    continue
                except Exception as e:
                    self.fail(f"Schema validation failed: {str(e)}")
            if i >= 50:  # Safeguard to avoid infinite loops in case of an issue
                break

if __name__ == '__main__':
    unittest.main()
