import unittest
import random
import string
import uuid
import requests
from server.app.models.usercontext.usercontext_post_request import UserContextPostRequestModel
from server.app.models.usercontext.usercontext_response import ContextDataItem
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

    def create_user_context(self, thread_id, context_data):
        """
        Creates a user context with the provided thread_id and context_data.
        Uses the test user ID created in setUpClass.
        """
        payload = UserContextPostRequestModel(
            user=self.test_user_id,
            thread_id=thread_id,
            context_data=context_data
        )

        # Convert UUID to string for JSON serialization
        payload_dict = payload.dict()

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
        """
        Creates a test prompt object. In this case, we will not interact with prompts directly
        but rather with context data, which can be structured similarly.
        """
        return str(uuid.uuid4())  # Generate a UUID for the prompt as a placeholder

    def test_create_and_get_user_context(self):
        # Create a test prompt and get its UUID
        prompt_uuid = self.create_test_prompt()
        thread_id = 1  # Assume a valid thread ID for testing
        context_data = [
            ContextDataItem(
                prompt="Test prompt",
                user=self.test_user_id,
                status="IN_PROGRESS",
                model="TestModel",
                completion={"id": prompt_uuid, "choices": [{"index": 0, "message": {"content": "Test message", "role": "assistant"}}]}
            ).dict()
        ]

        # Create a user context with the generated prompt UUID
        created_context = self.create_user_context(thread_id, context_data)

        # Retrieve user context by thread_id and user
        response = requests.get(f"{self.BASE_URL}/usercontext",
                                params={"thread_id": thread_id, "user": self.test_user_id})
        print(f"Get User Context Response Status Code: {response.status_code}")
        print(f"Get User Context Response Body: {response.text}")
        self.assertEqual(response.status_code, 200)
        context = response.json()

        # Assert that the created user context is retrieved
        self.assertEqual(context["user"], created_context["user"])

    def test_delete_user_context(self):
        prompt_uuid = self.create_test_prompt()

        thread_id = 1  # Assume a valid thread ID for testing
        context_data = [
            ContextDataItem(
                prompt="Test prompt",
                user=self.test_user_id,
                status="IN_PROGRESS",
                model="TestModel",
                completion={"id": prompt_uuid, "choices": [{"index": 0, "message": {"content": "Test message", "role": "assistant"}}]}
            ).dict()
        ]

        created_context = self.create_user_context(thread_id, context_data)

        # Ensure the context is created
        response = requests.get(f"{self.BASE_URL}/usercontext",
                                params={"thread_id": thread_id, "user": self.test_user_id})
        print(f"Get User Context Before Delete Status Code: {response.status_code}")
        print(f"Get User Context Before Delete Body: {response.text}")
        self.assertEqual(response.status_code, 200)
        context = response.json()

        self.assertEqual(context["id"], created_context["id"])

        # Delete the context
        self.delete_user_context(created_context["id"])

        # Ensure the context is deleted
        response = requests.get(f"{self.BASE_URL}/usercontext",
                                params={"thread_id": thread_id, "user": self.test_user_id})
        print(f"Get User Context After Delete Status Code: {response.status_code}")
        print(f"Get User Context After Delete Body: {response.text}")
        self.assertEqual(response.status_code, 404)

if __name__ == '__main__':
    unittest.main()
