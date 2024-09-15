import unittest
import random
import string
import uuid
import requests
from fastapi.encoders import jsonable_encoder
from server.app.models.usercontext.usercontext_post_request_model import UserContextPostRequestModel, ContextDataItem
from server.app.models.usercontext.usercontext_post_request_model import UserContextPrompt
from server.app.config.settings import Settings
from server.app.models.users.users_post_request import UserPostRequestModel
from server.tests.test_abstract import TestAbstract
import asyncio

class TestUserContext(TestAbstract):
    @classmethod
    def setUpClass(cls):
        """Synchronous setup, including the API key retrieval and admin user details."""
        cls.settings = Settings()
        cls.BASE_URL = cls.settings.get("default").get("SERVER_URL")
        cls.APP_DEFAULT_ADMIN_USERNAME = cls.settings.get("default").get("APP_DEFAULT_ADMIN_USERNAME")

        # Manually run async initialization using asyncio.run() to retrieve API key
        asyncio.run(cls.async_init())

        # Fetch the first user UUID or create a test user
        cls.test_user_uuid = cls.get_first_user_uuid()

    @classmethod
    def get_first_user_uuid(cls):
        """Fetch the first user from the database."""
        response = requests.get(f"{cls.BASE_URL}/users?api_key={cls.api_key}")
        if response.status_code != 200:
            raise AssertionError(f"Failed to fetch users: {response.text}")

        users = response.json()
        if not users:
            return cls.create_test_user()

        return str(users[0]['uuid'])  # Ensure UUID is a string

    @classmethod
    def create_test_user(cls):
        """Create a test user if none exists."""
        username = cls.generate_random_string()
        email = f"{cls.generate_random_string()}@example.com"
        create_payload = UserPostRequestModel(
            username=username,
            email=email
        )
        response = requests.post(f"{cls.BASE_URL}/users?api_key={cls.api_key}", json=create_payload.model_dump())
        if response.status_code != 201:
            raise AssertionError(f"Failed to create test user: {response.text}")
        return response.json().get('uuid')

    @classmethod
    def generate_random_string(cls, length=10):
        """Generate a random string of given length."""
        return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

    def create_test_prompt_data(self):
        """
        Creates test data for the prompt object using UserContextPrompt.
        """
        return UserContextPrompt(
            uuid=str(uuid.uuid4()),  # Convert UUID to string
            prompt="Test prompt",
            user=self.test_user_uuid,  # Use test user's UUID
            status="IN_PROGRESS",
            context_data=[  # Realistic context data
                ContextDataItem(
                    id=uuid.uuid4(),  # Generate a UUID for context item
                    user=self.test_user_uuid,  # Use test user UUID
                    status="COMPLETED",  # Example status
                    model="TestModel",  # Example model
                    completion={
                        "id": str(uuid.uuid4()),  # Completion ID
                        "choices": [
                            {
                                "index": 0,
                                "message": {
                                    "content": "Test completion message",
                                    "role": "assistant"
                                }
                            }
                        ]
                    }
                ).model_dump()  # Convert context data to dict
            ]
        ).model_dump()  # Updated from dict()

    def create_user_context(self, thread_id, context_data_list, prompt_data_list):
        """
        Creates multiple user contexts with the provided thread_id, context_data, and prompt_data.
        Uses the test user UUID created in setUpClass.
        """
        user_contexts = []
        for prompt_data, context_data in zip(prompt_data_list, context_data_list):
            payload = UserContextPostRequestModel(
                uuid=str(uuid.uuid4()),  # Generate a new UUID for the context
                user=self.test_user_uuid,  # Use the test user UUID
                thread_id=thread_id,
                prompt=UserContextPrompt(**prompt_data),  # Prompt data passed correctly as UserContextPrompt
                context_data=context_data  # Add the context data
            )
            user_contexts.append(payload.model_dump())  # Updated from dict()

        # Ensure proper encoding of UUIDs using jsonable_encoder
        payload_list = jsonable_encoder(user_contexts)

        response = requests.post(f"{self.BASE_URL}/usercontext?api_key={self.api_key}", json=payload_list)
        if response.status_code != 200:
            print(f"Create User Context Response: {response.text}")  # Debugging output
        self.assertEqual(response.status_code, 200)
        return response.json()

    def test_create_and_get_user_contexts(self):
        # Create test prompt data
        prompt_data_list = [self.create_test_prompt_data() for _ in range(2)]  # Create two sets of prompt data

        # Context and thread setup
        thread_id = 1
        context_data_list = [
            [
                ContextDataItem(
                    id=uuid.uuid4(),  # Generate a new UUID for the context item
                    user=self.test_user_uuid,  # UUID for the user
                    status="IN_PROGRESS",
                    model="TestModel",
                    completion={"id": str(uuid.uuid4()),
                                "choices": [{"index": 0, "message": {"content": "Test message", "role": "assistant"}}]}
                ).model_dump()  # Updated from dict()
            ] for _ in range(2)  # Create context data for two different user contexts
        ]

        # Log and validate the user context creation process
        try:
            created_contexts = self.create_user_context(thread_id, context_data_list, prompt_data_list)

            # Retrieve user contexts by thread_id and user
            response = requests.get(f"{self.BASE_URL}/usercontext",
                                    params={"thread_id": thread_id, "user": self.test_user_uuid, "api_key": self.api_key})
            self.assertEqual(response.status_code, 200)
            contexts = response.json()

            # Validate that the context data and prompt are correct for multiple contexts
            for idx, context in enumerate(contexts):
                self.assertEqual(context["user"], created_contexts[idx]["user"])
                self.assertEqual(context["prompt"]["uuid"], prompt_data_list[idx]["uuid"])

        except AssertionError as e:
            print(f"Unexpected status code: {e}")

if __name__ == '__main__':
    unittest.main()
