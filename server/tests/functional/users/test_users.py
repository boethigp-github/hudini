import unittest
import requests
import random
from server.app.config.settings import Settings
from server.app.models.users.users_get_response import UsersGetResponseModel
from server.app.models.users.users_post_request import UserPostRequestModel

class TestUsers(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Initialize the settings
        cls.settings = Settings()

        # Set the BASE_URL from the loaded configuration
        cls.BASE_URL = cls.settings.get("default").get("SERVER_URL")

    def create_test_user(self):
        # Generate a random username and email for testing
        random_number = random.randint(1, 1000000)  # For uniqueness
        username = f"user_{random_number}"  # Random username
        email = f"user{random_number}@example.com"  # Random email
        create_payload = UserPostRequestModel(
            username=username,
            email=email
        )
        create_response = requests.post(f"{self.BASE_URL}/users", json=create_payload.model_dump())
        self.assertEqual(create_response.status_code, 200)
        return create_response.json()['id']  # Expect the response to include the user ID

    def delete_user(self, user_id):
        delete_response = requests.delete(f"{self.BASE_URL}/users/{user_id}")
        self.assertEqual(delete_response.status_code, 200)
        delete_data = delete_response.json()
        self.assertEqual(delete_data['status'], "User deleted successfully")

    def validate_user(self, user_data):
        try:
            UsersGetResponseModel.model_validate(user_data)
        except ValueError as e:
            self.fail(f"Response validation failed: {e}")

    def test_get_all_users(self):
        response = requests.get(f"{self.BASE_URL}/users")
        self.assertEqual(response.status_code, 200)
        users = response.json()
        self.assertIsInstance(users, list)
        for user in users:
            self.validate_user(user)

    def test_get_user_by_id(self):
        user_id = self.create_test_user()

        response = requests.get(f"{self.BASE_URL}/users/{user_id}")
        self.assertEqual(response.status_code, 200)
        user = response.json()
        self.validate_user(user)

        # Clean up
        self.delete_user(user_id)

    def test_get_user_by_id_not_found(self):
        non_existent_id = random.randint(1000001, 2000000)  # ID not likely to exist
        response = requests.get(f"{self.BASE_URL}/users/{non_existent_id}")
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json()["detail"], f"User with id {non_existent_id} not found")

    def test_delete_user(self):
        user_id = self.create_test_user()

        response = requests.delete(f"{self.BASE_URL}/users/{user_id}")
        self.assertEqual(response.status_code, 200)
        delete_data = response.json()
        self.assertEqual(delete_data['status'], "User deleted successfully")

        # Verify deletion
        response = requests.get(f"{self.BASE_URL}/users/{user_id}")
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json()["detail"], f"User with id {user_id} not found")

    def test_delete_user_not_found(self):
        non_existent_id = random.randint(1000001, 2000000)  # ID not likely to exist
        response = requests.delete(f"{self.BASE_URL}/users/{non_existent_id}")
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json()["detail"], f"User with id {non_existent_id} not found")

if __name__ == '__main__':
    unittest.main()
