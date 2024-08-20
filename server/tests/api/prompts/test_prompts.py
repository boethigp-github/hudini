import unittest
import requests
import os
import uuid
import sys
from dotenv import load_dotenv
from jsonschema import validate, ValidationError

# Get the current file's directory
current_dir = os.path.dirname(os.path.abspath(__file__))

# Add the server directory to sys.path to allow importing the app module
sys.path.append(os.path.join(current_dir, '..', '..', '..'))

from server.app import SchemaToModelBuilder

# Construct the path to .env.local
env_path = os.path.join(current_dir, '..', '..','..', '.env.local')

# Load environment variables from .env.local
load_dotenv(env_path)

class TestPrompts(unittest.TestCase):
    BASE_URL = os.getenv('SERVER_URL', 'http://localhost:5000')

    @classmethod
    def setUpClass(cls):
        # Load the Swagger definition and Prompt schema
        schema_ref = SchemaToModelBuilder.load_swagger_definition()
        cls.prompt_schema = schema_ref['components']['schemas']['Prompt']

    def validate_response(self, data):
        try:
            validate(instance=data, schema=self.prompt_schema)
        except ValidationError as e:
            self.fail(f"Response validation failed: {e.message}")

    def test_load_prompts(self):
        response = requests.get(f"{self.BASE_URL}/load_prompts")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIsInstance(data, list)

        for prompt in data:
            self.validate_response(prompt)

    def test_create_and_delete_prompt(self):
        # Generate a new UUID for the prompt
        new_id = str(uuid.uuid4())

        # Test creating a new prompt with a specific ID
        create_payload = {
            "id": new_id,
            "user": "testuser",  # User field is required
            "prompt": "Test prompt",  # Prompt field is required
            "status": "initialized"  # Status field is required and must match enum
        }
        create_response = requests.post(f"{self.BASE_URL}/create_prompt", json=create_payload)

        if create_response.status_code != 200:
            print("Response content:", create_response.text)

        self.assertEqual(create_response.status_code, 200)
        create_data = create_response.json()

        # Validate the response against the Prompt schema
        self.validate_response(create_data)

        # Ensure the ID matches the one provided
        self.assertEqual(create_data['id'], new_id)

        # Test deleting the created prompt using the same ID
        delete_response = requests.delete(f"{self.BASE_URL}/delete_prompt/{new_id}")
        self.assertEqual(delete_response.status_code, 200)
        delete_data = delete_response.json()
        self.assertEqual(delete_data['status'], "Prompt deleted successfully")

    def test_create_prompt_validation(self):
        # Test creating a prompt with invalid payload (missing required fields)
        invalid_payload = {"user": "testuser"}  # Missing 'prompt' and 'status'
        response = requests.post(f"{self.BASE_URL}/create_prompt", json=invalid_payload)
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertEqual(data['status'], "validation-error")

    def test_invalid_status_in_prompt(self):
        # Test creating a prompt with an invalid status value
        invalid_payload = {
            "id": str(uuid.uuid4()),
            "user": "testuser",
            "prompt": "Test prompt",
            "status": "invalid-status"  # This is not in the enum
        }
        response = requests.post(f"{self.BASE_URL}/create_prompt", json=invalid_payload)
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertEqual(data['status'], "validation-error")
        print("Invalid status test passed")

    def test_update_prompt_validation(self):
        # Load existing prompts to get a valid ID
        response = requests.get(f"{self.BASE_URL}/load_prompts")
        self.assertEqual(response.status_code, 200)
        prompts = response.json()

        if not prompts:
            # No prompts available, create one first with a specific UUID
            new_id = str(uuid.uuid4())  # Generate a new UUID
            create_payload = {"id": new_id, "user": "testuser", "prompt": "Original prompt", "status": "initialized"}
            create_response = requests.post(f"{self.BASE_URL}/create_prompt", json=create_payload)
            self.assertEqual(create_response.status_code, 200)
            id = create_response.json()['id']
            self.assertEqual(id, new_id)  # Ensure the created ID matches the UUID we provided
        else:
            # Use the ID of the first prompt in the list
            id = prompts[0]['id']

        # Attempt to update with invalid data (missing 'prompt' and 'status')
        invalid_payload = {"user": "testuser"}  # Missing 'prompt' and 'status'
        update_response = requests.patch(f"{self.BASE_URL}/update_prompt/{id}", json=invalid_payload)
        self.assertEqual(update_response.status_code, 400)
        update_data = update_response.json()
        self.assertEqual(update_data['status'], "validation-error")

        # Clean up by deleting the prompt
        delete_response = requests.delete(f"{self.BASE_URL}/delete_prompt/{id}")
        self.assertEqual(delete_response.status_code, 200)


if __name__ == '__main__':
    unittest.main()
