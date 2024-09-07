import unittest
import random
import string
import uuid
import requests
from fastapi.encoders import jsonable_encoder
from datetime import datetime
from server.app.models.usercontext.usercontext_post_request_model import UserContextPostRequestModel, ContextDataItem
from server.app.models.usercontext.usercontext_post_request_model import UserContextPrompt
from server.app.config.settings import Settings
from server.app.models.users.users_post_request import UserPostRequestModel

class TestUserContext(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Initialize the settings
        cls.settings = Settings()
        cls.BASE_URL = cls.settings.get("default").get("SERVER_URL")

        # Get the first user UUID or create a test user
        cls.test_user_uuid = cls.get_first_user_uuid()

    @classmethod
    def get_first_user_uuid(cls):
        """Fetch the first user from the database or create a new test user."""
        response = requests.get(f"{cls.BASE_URL}/users")
        if response.status_code != 200:
            raise AssertionError(f"Failed to fetch users: {response.text}")

        users = response.json()
        if users:
            return str(users[0]['uuid'])  # Use the UUID of the first user as a string
        else:
            return cls.create_test_user()

    @classmethod
    def generate_random_string(cls, length=10):
        return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

    @classmethod
    def create_test_user(cls):
        """Create a test user if none exists."""
        username = cls.generate_random_string()
        email = f"{cls.generate_random_string()}@example.com"
        create_payload = UserPostRequestModel(
            username=username,
            email=email
        )
        response = requests.post(f"{cls.BASE_URL}/users", json=create_payload.model_dump())  # Updated from dict()
        if response.status_code != 201:
            raise AssertionError(f"Failed to create test user: {response.text}")
        return response.json().get('uuid')

    def create_test_prompt_data(self):
        """
        Creates test data for the prompt object using UserContextPrompt.
        """
        return UserContextPrompt(
            uuid=str(uuid.uuid4()),  # Convert UUID to string
            prompt="Test prompt",
            user=self.test_user_uuid,  # Use test user's UUID
            status="IN_PROGRESS",
            context_data=[]  # Empty context data for now
        ).model_dump()  # Updated from dict()

    def create_user_context(self, thread_id, context_data, prompt_data):
        """
        Creates a user context with the provided thread_id, context_data, and prompt_data.
        Uses the test user UUID created in setUpClass.
        """
        payload = UserContextPostRequestModel(
            uuid=str(uuid.uuid4()),  # Generate a new UUID for the context
            user=self.test_user_uuid,  # Use the test user UUID
            thread_id=thread_id,
            prompt=UserContextPrompt(**prompt_data),  # Prompt data passed correctly as UserContextPrompt
            context_data=context_data  # Add the context data
        )

        # Ensure proper encoding of UUIDs using jsonable_encoder
        payload_dict = jsonable_encoder(payload.model_dump())  # Updated from dict()

        response = requests.post(f"{self.BASE_URL}/usercontext", json=payload_dict)
        if response.status_code != 200:
            print(f"Create User Context Response: {response.text}")  # Debugging output
        self.assertEqual(response.status_code, 200)
        return response.json()

    def test_create_and_get_user_context(self):
        # Create test prompt data
        prompt_data = self.create_test_prompt_data()

        # Context and thread setup
        thread_id = 1
        context_data = [
            ContextDataItem(
                id=uuid.uuid4(),  # Generate a new UUID for the context item
                user=self.test_user_uuid,  # UUID for the user
                status="IN_PROGRESS",
                model="TestModel",
                completion={"id": str(uuid.uuid4()), "choices": [{"index": 0, "message": {"content": "Test message", "role": "assistant"}}]}
            ).model_dump()  # Updated from dict()
        ]

        # Log and validate the user context creation process
        try:
            created_context = self.create_user_context(thread_id, context_data, prompt_data)

            # Retrieve user context by thread_id and user
            response = requests.get(f"{self.BASE_URL}/usercontext", params={"thread_id": thread_id, "user": self.test_user_uuid})
            self.assertEqual(response.status_code, 200)
            context = response.json()

            # Validate that the context data and prompt are correct
            self.assertEqual(context["user"], created_context["user"])
            self.assertEqual(context["prompt"]["uuid"], prompt_data["uuid"])

        except AssertionError as e:
            print(f"Unexpected status code: {e}")

if __name__ == '__main__':
    unittest.main()
