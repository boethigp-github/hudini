import unittest
import requests
import uuid
from jsonschema import validate, ValidationError
from server.app.utils.swagger_loader import SwaggerLoader
from server.app.config.settings import Settings  # Adjust the import path according to your project structure

class TestPrompts(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Initialize the settings
        cls.settings = Settings()

        # Set the BASE_URL from the loaded configuration
        cls.BASE_URL = cls.settings.get("default").get("SERVER_URL")

        # Load the prompt schema using SwaggerLoader
        cls.prompt_schema = SwaggerLoader("swagger.yaml").get_component_schema("Prompt")

    def validate_response(self, data):
        try:
            validate(instance=data, schema=self.prompt_schema)
        except ValidationError as e:
            self.fail(f"Response validation failed: {e.message}")

    def create_test_prompt(self):
        new_id = str(uuid.uuid4())
        create_payload = {"id": new_id, "user": new_id, "prompt": "Test prompt", "status": "initialized"}
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


    def test_invalid_status_in_creatprompt(self):
        invalid_payload = {
            "id": str(uuid.uuid4()),
            "user": "testuser",
            "prompt": "Test prompt",
            "status": "invalid-status"
        }
        response = requests.post(f"{self.BASE_URL}/prompt", json=invalid_payload)
        self.assertEqual(response.status_code, 400)


if __name__ == '__main__':
    unittest.main()
