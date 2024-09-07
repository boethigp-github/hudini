import unittest
import random
import string
import uuid
import requests
from fastapi.encoders import jsonable_encoder
from datetime import datetime
from server.app.models.usercontext.usercontext_post_request_model import UserContextPostRequestModel, ContextDataItem
from server.app.models.prompts.prompt_post_response_model import PromptPostResponseModel
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

    def create_test_prompt_data(self):
        """
        Creates test data for the prompt object using PromptHttpModel.
        """
        return PromptPostResponseModel(
            id=1,
            prompt="Test prompt",
            user=self.test_user_id,
            status="IN_PROGRESS",
            created=int(datetime.utcnow().timestamp()),  # Correct handling of timestamp
            uuid=uuid.uuid4()
        ).dict()

    def create_user_context(self, thread_id, context_data, prompt_data):
        """
        Creates a user context with the provided thread_id, context_data, and prompt_data.
        Uses the test user ID created in setUpClass.
        """
        payload = UserContextPostRequestModel(
            user=self.test_user_id,
            thread_id=thread_id,
            prompt=PromptPostResponseModel(**prompt_data),
            context_data=context_data
        )

        # Use jsonable_encoder to ensure proper encoding of UUIDs
        payload_dict = jsonable_encoder(payload.dict())

        response = requests.post(f"{self.BASE_URL}/usercontext", json=payload_dict)
        if response.status_code != 200:
            print(f"Create User Context Response: {response.text}")  # Debugging output
        self.assertEqual(response.status_code, 200)
        return response.json()

    def test_create_and_get_user_context(self):
        # Create test prompt data
        prompt_data = self.create_test_prompt_data()

        thread_id = 1
        context_data = [
            ContextDataItem(
                user=self.test_user_id,
                status="IN_PROGRESS",
                model="TestModel",
                completion={"id": str(uuid.uuid4()), "choices": [{"index": 0, "message": {"content": "Test message", "role": "assistant"}}]}
            ).dict()
        ]

        # Log and validate the user context creation process
        try:
            created_context = self.create_user_context(thread_id, context_data, prompt_data)

            # Retrieve user context by thread_id and user
            response = requests.get(f"{self.BASE_URL}/usercontext", params={"thread_id": thread_id, "user": self.test_user_id})
            self.assertEqual(response.status_code, 200)
            context = response.json()

            # Validate that the context data and prompt are correct
            self.assertEqual(context["user"], created_context["user"])
            self.assertEqual(context["prompt"]["id"], prompt_data["id"])

        except AssertionError as e:
            print(f"Unexpected status code: {e}")

if __name__ == '__main__':
    unittest.main()
