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

class TestPrompts(unittest.TestCase):
    BASE_URL = os.getenv('SERVER_URL', 'http://localhost:5000')

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

if __name__ == '__main__':
    unittest.main()
