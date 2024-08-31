import unittest
import requests
import uuid
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

    def create_user_context(self, thread_id, user_id=None, prompt_id=None, context_data=None):
        user_id = user_id or str(uuid.uuid4())
        prompt_id = prompt_id or str(uuid.uuid4())  # Generate a new UUID for prompt_id if not provided
        context_data = context_data or [{"key": "value"}]  # Default context data

        # Use the request model to create the payload
        payload = UserContextPostRequestModel(
            user=user_id,
            thread_id=thread_id,
            prompt_id=prompt_id,
            context_data=context_data
        )

        # Convert the UUID fields to strings before sending the request
        payload_dict = payload.model_dump()
        payload_dict['user'] = str(payload.user)
        payload_dict['prompt_id'] = str(payload.prompt_id)

        # Convert the model to a dictionary before sending the request
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
        thread_id = 1
        created_context = self.create_user_context(thread_id)

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
        thread_id = 1
        created_context = self.create_user_context(thread_id)

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
