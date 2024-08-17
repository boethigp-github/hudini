import unittest
import requests
import os
from dotenv import load_dotenv

# Get the current file's directory
current_dir = os.path.dirname(os.path.abspath(__file__))

# Construct the path to .env.local
env_path = os.path.join(current_dir, '..', '..', '.env.local')

# Load environment variables from .env.local
load_dotenv(env_path)

class TestSavePromptValidation(unittest.TestCase):
    BASE_URL = os.getenv('SERVER_URL', 'http://localhost:5000')

    def test_save_prompt_valid(self):
        payload = {"prompt": "Test prompt"}
        response = requests.post(f"{self.BASE_URL}/save_prompt", json=payload)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('status', data)
        self.assertEqual(data['status'], "Prompt saved successfully")
        self.assertIn('id', data)

    def test_save_prompt_invalid_missing_prompt(self):
        payload = {}  # Missing 'prompt' field
        response = requests.post(f"{self.BASE_URL}/save_prompt", json=payload)
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertIn('error', data)
        self.assertIn("'prompt' is a required property", data['error'])

    def test_save_prompt_invalid_empty_prompt(self):
        payload = {"prompt": ""}
        response = requests.post(f"{self.BASE_URL}/save_prompt", json=payload)
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertIn('error', data)
        self.assertEqual(data['error'], "No prompt provided")

    def test_save_prompt_invalid_extra_field(self):
        payload = {"prompt": "Test prompt", "extra_field": "This shouldn't be here"}
        response = requests.post(f"{self.BASE_URL}/save_prompt", json=payload)
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertIn('error', data)
        self.assertIn("Additional properties are not allowed", data['error'])

if __name__ == '__main__':
    unittest.main()
