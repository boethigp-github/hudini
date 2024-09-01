import unittest
import requests
from server.app.config.settings import Settings
from server.app.models.usercontext.usercontext_post_request import UserContextPostRequestModel
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
    def create_test_user(cls):
        # Create a test user through the API
        username = "test_user"
        email = "test_user@example.com"
        payload = UserPostRequestModel(
            username=username,
            email=email
        )
        response = requests.post(f"{cls.BASE_URL}/users", json=payload.model_dump())
        if response.status_code != 200:
            print("Create User Response:", response.text)  # Debugging output
        assert response.status_code == 200, f"Expected status code 200 but got {response.status_code}"
        user_data = response.json()
        return user_data['id']

    def create_user_context(self, thread_id, prompt_id, context_data):
        """
        Creates a user context with the provided thread_id, prompt_id, and context_data.
        Uses the test user ID created in setUpClass.
        """
        payload = UserContextPostRequestModel(
            user=self.test_user_id,
            thread_id=thread_id,
            prompt_id=prompt_id,
            context_data=context_data
        )

        payload_dict = payload.model_dump()

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

    def test_create_and_get_user_context(self):
        # Generate valid prompt_id and thread_id
        prompt_id = 1  # Assume a valid prompt ID for testing
        thread_id = 1  # Assume a valid thread ID for testing
        context_data = [{"key": "value"}]  # Example context data

        created_context = self.create_user_context(thread_id, prompt_id, context_data)

        # Retrieve by thread_id and user
        response = requests.get(f"{self.BASE_URL}/usercontext",
                                params={"thread_id": thread_id, "user": self.test_user_id})
        print(f"Get User Context Response Status Code: {response.status_code}")
        print(f"Get User Context Response Body: {response.text}")
        self.assertEqual(response.status_code, 200)
        contexts = response.json()

        self.assertTrue(any(context["user"] == created_context["user"] for context in contexts))

        # Cleanup
        self.delete_user_context(created_context["id"])

    def test_delete_user_context(self):
        # Generate valid prompt_id and thread_id
        prompt_id = 1  # Assume a valid prompt ID for testing
        thread_id = 1  # Assume a valid thread ID for testing
        context_data = [{"key": "value"}]  # Example context data

        created_context = self.create_user_context(thread_id, prompt_id, context_data)

        # Ensure the context is created
        response = requests.get(f"{self.BASE_URL}/usercontext",
                                params={"thread_id": thread_id, "user": self.test_user_id})
        print(f"Get User Context Before Delete Status Code: {response.status_code}")
        print(f"Get User Context Before Delete Body: {response.text}")
        self.assertEqual(response.status_code, 200)
        contexts = response.json()
        self.assertTrue(any(context["id"] == created_context["id"] for context in contexts))

        # Now delete the created context
        self.delete_user_context(created_context["id"])

        # Verify deletion
        response = requests.get(f"{self.BASE_URL}/usercontext",
                                params={"thread_id": thread_id, "user": self.test_user_id})
        print(f"Get User Context After Delete Status Code: {response.status_code}")
        print(f"Get User Context After Delete Body: {response.text}")
        self.assertEqual(response.status_code, 404)  # Should return 404 since the context was deleted

if __name__ == '__main__':
    unittest.main()
