import unittest
import requests
import random
import string
import uuid
from server.app.config.settings import Settings
from server.app.models.prompts.prompt_post_request_model import PromptPostRequestModel


class TestPrompts(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.settings = Settings()
        cls.BASE_URL = cls.settings.get("default").get("SERVER_URL")
        cls.TEST_USER_UUID = cls.get_first_user_uuid()

    @classmethod
    def get_first_user_uuid(cls):
        """Fetch the first user from the database."""
        response = requests.get(f"{cls.BASE_URL}/users")
        if response.status_code != 200:
            raise AssertionError(f"Failed to fetch users: {response.text}")

        users = response.json()
        if not users:
            raise AssertionError("No users found in the database")

        return str(users[0]['uuid'])  # Ensure UUID is a string

    def create_test_prompt(self):
        """Create a test prompt with UUID properly serialized as string."""
        if not self.TEST_USER_UUID:
            raise AssertionError("TEST_USER_UUID is None, cannot create test prompt")

        # Create the payload with UUIDs as strings
        create_payload = PromptPostRequestModel(
            prompt="Test prompt",
            user=self.TEST_USER_UUID,  # UUID passed as string here
            status="IN_PROGRESS",
            uuid=str(uuid.uuid4())  # Ensure UUID is stringified
        )

        # Convert the model to a dictionary and ensure all UUIDs are strings
        payload_dict = create_payload.model_dump()
        payload_dict = {k: str(v) if isinstance(v, uuid.UUID) else v for k, v in payload_dict.items()}

        # Send the POST request
        create_response = requests.post(f"{self.BASE_URL}/prompts", json=payload_dict)

        # Check for successful creation
        if create_response.status_code != 201:
            raise AssertionError(f"Failed to create test prompt: {create_response.text}")

        # Return the UUID of the newly created prompt
        return create_response.json().get('uuid')

    def test_create_and_delete_prompt(self):
        """Test creating a new prompt and deleting it."""
        # Create a new test prompt
        new_uuid = self.create_test_prompt()

        # Validate prompt creation by checking if it appears in the list of prompts
        response = requests.get(f"{self.BASE_URL}/prompts")
        if response.status_code != 200:
            raise AssertionError(f"Failed to get prompts after creation: {response.text}")
        prompts = response.json()
        self.assertTrue(any(prompt['uuid'] == new_uuid for prompt in prompts), "Prompt not found after creation")

        # Delete the newly created prompt
        self.delete_prompt(new_uuid)

        # Validate prompt deletion by checking if it's removed from the list
        response = requests.get(f"{self.BASE_URL}/prompts")
        if response.status_code != 200:
            raise AssertionError(f"Failed to get prompts after deletion: {response.text}")
        prompts = response.json()
        self.assertFalse(any(prompt['uuid'] == new_uuid for prompt in prompts), "Prompt still found after deletion")

    def delete_prompt(self, prompt_uuid):
        """Delete the given prompt by UUID."""
        delete_response = requests.delete(f"{self.BASE_URL}/prompts/{prompt_uuid}")
        if delete_response.status_code != 200:
            raise AssertionError(f"Failed to delete prompt: {delete_response.text}")
        delete_data = delete_response.json()
        if delete_data.get('status') != "Prompt deleted successfully":
            raise AssertionError(f"Unexpected response for prompt deletion: {delete_data}")


if __name__ == '__main__':
    unittest.main()
