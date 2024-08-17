import unittest
import requests
import json
import yaml
from dotenv import load_dotenv
import os

# Get the current file's directory
current_dir = os.path.dirname(os.path.abspath(__file__))

# Construct the path to .env.local
env_path = os.path.join(current_dir, '..', '..', '.env.local')

# Load environment variables from .env.local
load_dotenv(env_path)

class TestLlamaCppChatAPI(unittest.TestCase):
    BASE_URL = os.getenv('SERVER_URL', 'http://localhost:5000')

    def test_get_models(self):
        response = requests.get(f"{self.BASE_URL}/get_models")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('local_models', data)
        self.assertIn('openai_models', data)
        self.assertIsInstance(data['local_models'], list)
        self.assertIsInstance(data['openai_models'], list)

    def test_generate(self):
        payload = {
            "prompt": "What is the capital of France?",
            "model": "gpt-3.5-turbo"  # Adjust this to a model you know exists
        }
        response = requests.post(f"{self.BASE_URL}/generate", json=payload)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('status', data)
        self.assertEqual(data['status'], "Prompt and model received")

    def test_stream(self):
        # First, send a generate request
        generate_payload = {
            "prompt": "Tell me a short joke",
            "model": "gpt-3.5-turbo"  # Adjust this to a model you know exists
        }
        requests.post(f"{self.BASE_URL}/generate", json=generate_payload)

        # Then, test the stream endpoint
        response = requests.get(f"{self.BASE_URL}/stream", stream=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers['Content-Type'], 'text/event-stream')

        # Read a few events to check if streaming works
        event_data = []
        for i, line in enumerate(response.iter_lines()):
            if line:
                event_data.append(line.decode('utf-8'))
            if i >= 5:  # Check first 5 non-empty lines
                break
        self.assertTrue(len(event_data) > 0)

    def test_load_prompts(self):
        response = requests.get(f"{self.BASE_URL}/load_prompts")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIsInstance(data, list)

    def test_save_and_delete_prompt(self):
        # Test saving a prompt
        save_payload = {"prompt": "Test prompt"}
        save_response = requests.post(f"{self.BASE_URL}/save_prompt", json=save_payload)
        self.assertEqual(save_response.status_code, 200)
        save_data = save_response.json()
        self.assertIn('id', save_data)
        prompt_id = save_data['id']

        # Test deleting the saved prompt
        delete_response = requests.delete(f"{self.BASE_URL}/delete_prompt/{prompt_id}")
        self.assertEqual(delete_response.status_code, 200)
        delete_data = delete_response.json()
        self.assertEqual(delete_data['status'], "Prompt deleted successfully")

    def test_swagger_yaml(self):
        response = requests.get(f"{self.BASE_URL}/swagger.yaml")
        try:
            self.assertEqual(response.status_code, 200)
        except AssertionError:
            print(f"Error: Unexpected status code {response.status_code}")
            print("Response content:")
            print(response.text)
            raise

        try:
            self.assertEqual(response.headers['Content-Type'], 'application/x-yaml')
        except AssertionError:
            print(f"Error: Unexpected Content-Type {response.headers.get('Content-Type')}")
            raise

        # Parse the YAML content
        try:
            swagger_data = yaml.safe_load(response.text)
        except yaml.YAMLError as e:
            print(f"Failed to parse YAML: {e}")
            print("Response content:")
            print(response.text)
            self.fail(f"Failed to parse YAML: {e}")

        # Check for essential Swagger/OpenAPI elements
        try:
            self.assertIn('openapi', swagger_data)
            self.assertIn('info', swagger_data)
            self.assertIn('paths', swagger_data)
        except AssertionError as e:
            print(f"Error: Missing essential Swagger/OpenAPI elements")
            print("Parsed YAML content:")
            print(json.dumps(swagger_data, indent=2))
            raise


if __name__ == '__main__':
    unittest.main()
