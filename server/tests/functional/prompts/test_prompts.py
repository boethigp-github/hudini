import unittest
import requests
import random
import string
import uuid
from server.app.config.settings import Settings
from server.app.models.prompts.prompt_get_response import PromptGetResponseModel
from server.app.models.prompts.prompts_post_request import PromptPostRequestModel
from server.app.models.users.users_post_request import UserPostRequestModel

class TestPrompts(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.settings = Settings()
        cls.BASE_URL = cls.settings.get("default").get("SERVER_URL")
        cls.created_user_ids = []
        cls.TEST_USER_ID = cls.create_test_user()
        cls.created_user_ids.append(cls.TEST_USER_ID)

    @classmethod
    def tearDownClass(cls):
        for user_id in cls.created_user_ids:
            cls.delete_test_user(user_id)

    @classmethod
    def generate_random_string(cls, length=10):
        return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

    @classmethod
    def create_test_user(cls):
        username = cls.generate_random_string()
        email = f"{cls.generate_random_string()}@example.com"
        create_payload = UserPostRequestModel(
            username=username,
            email=email
        )
        response = requests.post(f"{cls.BASE_URL}/users", json=create_payload.dict())
        if response.status_code != 201:
            cls.assertTrue(False, f"Failed to create test user: {response.text}")
        return response.json().get('id')

    @classmethod
    def delete_test_user(cls, user_id):
        response = requests.delete(f"{cls.BASE_URL}/users/{user_id}")
        if response.status_code != 200:
            cls.assertTrue(False, f"Failed to delete test user: {response.text}")
        delete_data = response.json()
        if delete_data.get('status') != "User deleted successfully":
            cls.assertTrue(False, f"Unexpected response for user deletion: {delete_data}")

    def create_test_prompt(self):
        create_payload = PromptPostRequestModel(
            prompt="Test prompt",
            user=self.TEST_USER_ID,
            status="IN_PROGRESS",
            uuid=str(uuid.uuid4())  # Generate a UUID for the prompt
        )
        create_response = requests.post(f"{self.BASE_URL}/prompts", json=create_payload.dict())
        if create_response.status_code != 201:
            self.fail(f"Failed to create test prompt: {create_response.text}")
        return create_response.json().get('id')

    def delete_prompt(self, prompt_id):
        delete_response = requests.delete(f"{self.BASE_URL}/prompts/{prompt_id}")
        if delete_response.status_code != 200:
            self.fail(f"Failed to delete prompt: {delete_response.text}")
        delete_data = delete_response.json()
        if delete_data.get('status') != "Prompt deleted successfully":
            self.fail(f"Unexpected response for prompt deletion: {delete_data}")

    def validate_prompt(self, prompt_data):
        try:
            PromptGetResponseModel(**prompt_data)
        except ValueError as e:
            self.fail(f"Response validation failed: {e}")

    def test_get_prompts(self):
        response = requests.get(f"{self.BASE_URL}/prompts")
        if response.status_code != 200:
            self.fail(f"Failed to get prompts: {response.text}")
        prompts = response.json()
        self.assertIsInstance(prompts, list)
        for prompt in prompts:
            self.validate_prompt(prompt)

    def test_create_and_delete_prompt(self):
        new_id = self.create_test_prompt()

        response = requests.get(f"{self.BASE_URL}/prompts")
        if response.status_code != 200:
            self.fail(f"Failed to get prompts after creation: {response.text}")
        prompts = response.json()
        self.assertTrue(any(prompt['id'] == new_id for prompt in prompts), "Prompt not found after creation")

        self.delete_prompt(new_id)

        response = requests.get(f"{self.BASE_URL}/prompts")
        if response.status_code != 200:
            self.fail(f"Failed to get prompts after deletion: {response.text}")
        prompts = response.json()
        self.assertFalse(any(prompt['id'] == new_id for prompt in prompts), "Prompt still found after deletion")

    def test_invalid_status_in_create_prompt(self):
        invalid_payload = {
            "prompt": "Test prompt",
            "user": self.TEST_USER_ID,
            "status": "invalid-status",  # Invalid status
            "uuid": str(uuid.uuid4())  # Generate a UUID for the invalid prompt
        }
        response = requests.post(f"{self.BASE_URL}/prompts", json=invalid_payload)
        self.assertEqual(response.status_code, 422)

    def test_create_prompt_duplicate(self):
        create_payload = PromptPostRequestModel(
            prompt="Duplicate test prompt",
            user=self.TEST_USER_ID,
            status="IN_PROGRESS",
            uuid=str(uuid.uuid4())  # Generate a UUID for the duplicate test
        )
        response1 = requests.post(f"{self.BASE_URL}/prompts", json=create_payload.dict())
        if response1.status_code != 201:
            self.fail(f"Failed to create first prompt: {response1.text}")
        prompt_id = response1.json().get('id')

        response2 = requests.post(f"{self.BASE_URL}/prompts", json=create_payload.dict())
        if response2.status_code != 201:
            self.fail(f"Failed to create second prompt: {response2.text}")
        created_prompt = response2.json()
        self.assertEqual(created_prompt['id'], prompt_id, "Duplicate prompt IDs should match")

    def test_delete_nonexistent_prompt(self):
        non_existent_id = 999999
        response = requests.delete(f"{self.BASE_URL}/prompts/{non_existent_id}")
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json().get('detail'), f"Prompt with id {non_existent_id} not found")

if __name__ == '__main__':
    unittest.main()
