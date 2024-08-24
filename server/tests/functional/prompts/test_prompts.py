import unittest
import requests
import os
import uuid
from dotenv import load_dotenv
from jsonschema import validate, ValidationError

from server.app.utils.swagger_loader import SwaggerLoader

class TestPrompts(unittest.TestCase):
    BASE_URL = None

    @classmethod
    def setUpClass(cls):
        # Load environment variables
        current_dir = os.path.dirname(os.path.abspath(__file__))
        env_path = os.path.join(current_dir, '..', '..', '..','infrastructure','environment', '.env.local')
        load_dotenv(env_path)

        cls.BASE_URL = os.getenv('SERVER_URL', 'http://localhost:5000')
        cls.prompt_schema = SwaggerLoader("swagger.yaml").get_component_schema("Prompt")

    def validate_response(self, data):
        try:
            validate(instance=data, schema=self.prompt_schema)
        except ValidationError as e:
            self.fail(f"Response validation failed: {e.message}")

    def create_test_prompt(self):
        new_id = str(uuid.uuid4())
        create_payload = {"id": new_id, "user": "testuser", "prompt": "Test prompt", "status": "initialized"}
        create_response = requests.post(f"{self.BASE_URL}/prompt", json=create_payload)
        self.assertEqual(create_response.status_code, 200)
        return create_response.json()['id']

    def prompt(self, prompt_id):
        delete_response = requests.delete(f"{self.BASE_URL}/prompt/{prompt_id}")
        self.assertEqual(delete_response.status_code, 200)
        delete_data = delete_response.json()
        self.assertEqual(delete_data['status'], "Prompt deleted successfully")

    def test_prompts(self):
        response = requests.get(f"{self.BASE_URL}/prompt")
        self.assertEqual(response.status_code, 200)
        prompts = response.json()
        for prompt in prompts:
            self.validate_response(prompt)

    def test_create_and_prompt(self):
        new_id = self.create_test_prompt()

        response = requests.get(f"{self.BASE_URL}/prompt")
        self.assertEqual(response.status_code, 200)
        prompts = response.json()
        self.assertTrue(any(prompt['id'] == new_id for prompt in prompts))

        self.prompt(new_id)

        response = requests.get(f"{self.BASE_URL}/prompt")
        self.assertEqual(response.status_code, 200)
        prompts = response.json()
        self.assertFalse(any(prompt['id'] == new_id for prompt in prompts))

    def test_prompt_validation(self):
        prompt_id = self.create_test_prompt()

        invalid_payload = {"user": "testuser"}
        update_response = requests.patch(f"{self.BASE_URL}/prompt/{prompt_id}", json=invalid_payload)
        self.assertEqual(update_response.status_code, 400)
        update_data = update_response.json()
        self.assertEqual(update_data['status'], "validation-error")

        self.prompt(prompt_id)

    def test_invalid_status_in_prompt(self):
        invalid_payload = {
            "id": str(uuid.uuid4()),
            "user": "testuser",
            "prompt": "Test prompt",
            "status": "invalid-status"
        }
        response = requests.post(f"{self.BASE_URL}/prompt", json=invalid_payload)
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertEqual(data['status'], "validation-error")

        print("Invalid status test passed")

if __name__ == '__main__':
    unittest.main()