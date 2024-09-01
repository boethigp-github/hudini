import unittest
import requests
import random
from server.app.config.settings import Settings  # Adjust the import path according to your project structure
from server.app.models.usercontext.usercontext_post_request import \
    UserContextPostRequestModel  # Import the request model


class TestUserContext(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Initialize the settings
        cls.settings = Settings()

        # Set the BASE_URL from the loaded configuration
        cls.BASE_URL = cls.settings.get("default").get("SERVER_URL")

    def create_user_context(self, thread_id, user_id, prompt_id, context_data):
        """
        Creates a user context with the provided thread_id, user_id, prompt_id, and context_data.
        All parameters must be provided and cannot be None.
        """

        # Use the request model to create the payload
        payload = UserContextPostRequestModel(
            user=user_id,
            thread_id=thread_id,
            prompt_id=prompt_id,
            context_data=context_data
        )

        # Convert the model to a dictionary before sending the request
        payload_dict = payload.model_dump()

        # Send the request
        response = requests.post(f"{self.BASE_URL}/usercontext", json=payload_dict)
        if response.status_code != 200:
            print("Create User Context Response:", response.text)  # Debugging output
        self.assertEqual(response.status_code, 200)
        return response.json()

    def delete_user_context(self, user_context_id):
        response = requests.delete(f"{self.BASE_URL}/usercontext/{user_context_id}")
        print(f"Delete User Context Response Status Code: {response.status_code}")
        print(f"Delete User Context Response Body: {response.text}")
        self.assertEqual(response.status_code, 200)
        delete_data = response.json()
        self.assertEqual(delete_data['status'], "User context deleted successfully")

    def test_create_and_get_user_context(self):
        # Generate valid user_id and prompt_id
        user_id = random.randint(1, 1000000000)  # Generate a new bigint for user_id
        prompt_id = random.randint(1, 1000000000)  # Generate a new bigint for prompt_id
        context_data = [{"key": "value"}]  # Example context data

        thread_id = 1
        created_context = self.create_user_context(thread_id, user_id, prompt_id, context_data)

        # Retrieve by thread_id and user
        response = requests.get(f"{self.BASE_URL}/usercontext",
                                params={"thread_id": thread_id, "user": created_context["user"]})
        print(f"Get User Context Response Status Code: {response.status_code}")
        print(f"Get User Context Response Body: {response.text}")
        self.assertEqual(response.status_code, 200)
        contexts = response.json()

        self.assertTrue(any(context["user"] == created_context["user"] for context in contexts))

        # Cleanup
        self.delete_user_context(created_context["id"])

    def test_delete_user_context(self):
        # Generate valid user_id and prompt_id
        user_id = random.randint(1, 1000000000)  # Generate a new bigint for user_id
        prompt_id = random.randint(1, 1000000000)  # Generate a new bigint for prompt_id
        context_data = [{"key": "value"}]  # Example context data

        thread_id = 1
        created_context = self.create_user_context(thread_id, user_id, prompt_id, context_data)

        # Ensure the context is created
        response = requests.get(f"{self.BASE_URL}/usercontext",
                                params={"thread_id": thread_id, "user": created_context["user"]})
        print(f"Get User Context Before Delete Status Code: {response.status_code}")
        print(f"Get User Context Before Delete Body: {response.text}")
        self.assertEqual(response.status_code, 200)
        contexts = response.json()
        self.assertTrue(any(context["id"] == created_context["id"] for context in contexts))

        # Now delete the created context
        self.delete_user_context(created_context["id"])

        # Verify deletion
        response = requests.get(f"{self.BASE_URL}/usercontext",
                                params={"thread_id": thread_id, "user": created_context["user"]})
        print(f"Get User Context After Delete Status Code: {response.status_code}")
        print(f"Get User Context After Delete Body: {response.text}")
        self.assertEqual(response.status_code, 404)  # Should return 404 since the context was deleted


if __name__ == '__main__':
    unittest.main()
