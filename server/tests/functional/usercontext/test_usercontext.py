import unittest
import random
import string
import uuid
import requests
from server.app.models.usercontext.usercontext_post_request import UserContextPostRequestModel
from server.app.config.settings import Settings
from server.app.models.users.users_post_request import UserPostRequestModel

class TestUserContext(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Initialize the settings
        cls.settings = Settings()
        cls.BASE_URL = cls.settings.get("default").get("SERVER_URL")

        # Create a test user and store the ID
        cls.test_user_id = cls.create_test_user()

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

    def create_user_context(self, thread_id, prompt_uuid, context_data):
        """
        Creates a user context with the provided thread_id, prompt_id, and context_data.
        Uses the test user ID created in setUpClass.
        """
        payload = UserContextPostRequestModel(
            user=self.test_user_id,
            thread_id=thread_id,
            prompt_uuid=prompt_uuid,
            context_data=context_data
        )

        # Convert UUID to string for JSON serialization
        payload_dict = payload.dict()
        payload_dict['prompt_uuid'] = str(payload_dict['prompt_uuid'])

        response = requests.post(f"{self.BASE_URL}/usercontext", json=payload_dict)
        if response.status_code != 200:
            print("Create User Context Response:", response.text)  # Debugging output
        self.assertEqual(response.status_code, 200)
        return response.json()

    def delete_user_context(self, user_context_id):
        response = requests.delete(f"{self.BASE_URL}/usercontext/{user_context_id}")
        print(f"Delete User Context Response Status Code: {response.status_code}")
        print(f"Delete User Context Response Body: {response.text}")
        self.assertEqual(200, response.status_code)
        delete_data = response.json()
        self.assertEqual(delete_data['status'], "User context deleted successfully")

    def create_test_prompt(self):
        create_payload = {
            "prompt": "Test prompt",
            "user": self.test_user_id,
            "status": "IN_PROGRESS",
            "uuid": str(uuid.uuid4())  # Generate a UUID for the prompt
        }
        create_response = requests.post(f"{self.BASE_URL}/prompts", json=create_payload)
        if create_response.status_code != 201:
            self.fail(f"Failed to create test prompt: {create_response.text}")
        return create_response.json().get('uuid')

    def test_create_and_get_user_context(self):
        # Create a test prompt and get its UUID
        prompt_uuid = self.create_test_prompt()
        thread_id = 1  # Assume a valid thread ID for testing
        context_data = [{"key": "value"}]  # Example context data

        # Create a user context with the generated prompt UUID
        created_context = self.create_user_context(thread_id, prompt_uuid, context_data)

        # Retrieve user context by thread_id and user
        response = requests.get(f"{self.BASE_URL}/usercontext",
                                params={"thread_id": thread_id, "user": self.test_user_id})
        print(f"Get User Context Response Status Code: {response.status_code}")
        print(f"Get User Context Response Body: {response.text}")
        self.assertEqual(response.status_code, 200)
        contexts = response.json()

        # Assert that the created user context is retrieved
        self.assertTrue(any(context["user"] == created_context["user"] for context in contexts))

        # Cleanup: Delete the user context and prompt
        #self.delete_user_context(created_context["id"])

    def test_delete_user_context(self):
        prompt_uuid = self.create_test_prompt()
        # Generate valid prompt_id and thread_id

        thread_id = 1  # Assume a valid thread ID for testing
        context_data = [{"key": "value"}]  # Example context data

        created_context = self.create_user_context(thread_id, prompt_uuid, context_data)

        # Ensure the context is created
        response = requests.get(f"{self.BASE_URL}/usercontext",
                                params={"thread_id": thread_id, "user": self.test_user_id})
        print(f"Get User Context Before Delete Status Code: {response.status_code}")
        print(f"Get User Context Before Delete Body: {response.text}")
        self.assertEqual(response.status_code, 200)
        contexts = response.json()
        self.assertTrue(any(context["id"] == created_context["id"] for context in contexts))

        # Delete the context
        self.delete_user_context(created_context["id"])

        # Ensure the context is deleted
        response = requests.get(f"{self.BASE_URL}/usercontext",
                                params={"thread_id": thread_id, "user": self.test_user_id})
        print(f"Get User Context After Delete Status Code: {response.status_code}")
        print(f"Get User Context After Delete Body: {response.text}")
        self.assertEqual(response.status_code, 200)
        contexts = response.json()
        self.assertFalse(any(context["id"] == created_context["id"] for context in contexts))

if __name__ == '__main__':
    unittest.main()
