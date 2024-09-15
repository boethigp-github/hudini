import unittest
import requests
import os
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from server.app.config.settings import Settings
from server.app.models.gripsbox.gripsbox_post_request import GripsboxPostRequestModel
from server.app.models.users.user import User


class TestGripsbox(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.settings = Settings()
        cls.BASE_URL = cls.settings.get("default").get("SERVER_URL")
        cls.APP_STORAGE = cls.settings.get("default").get("APP_STORAGE")
        cls.APP_DEFAULT_ADMIN_USERNAME = cls.settings.get("default").get("APP_DEFAULT_ADMIN_USERNAME")
        cls.TEST_FILE = "test_file.txt"

        # Setup DB connection and session
        cls.engine = create_engine(cls.settings.get("default").get("DATABASE_URL"))
        cls.Session = sessionmaker(bind=cls.engine)
        cls.session = cls.Session()

        # Retrieve the API key for the default admin user
        cls.api_key = cls.get_api_key_for_admin()

        cls.create_test_file()

    @classmethod
    def get_api_key_for_admin(cls):
        """Helper method to retrieve API key for the default admin user."""
        # Query the admin user by username
        admin_user = cls.session.query(User).filter_by(username=cls.APP_DEFAULT_ADMIN_USERNAME).first()
        if not admin_user:
            raise ValueError(f"Admin user {cls.APP_DEFAULT_ADMIN_USERNAME} not found.")

        # Get the active API key via the relationship
        api_key = admin_user.api_keys.filter_by(active=True).first()
        if not api_key:
            raise ValueError(f"No active API key found for user {cls.APP_DEFAULT_ADMIN_USERNAME}.")

        return api_key.key

    @classmethod
    def create_test_file(cls):
        """Helper method to create a test file."""
        with open(cls.TEST_FILE, "wb") as f:
            f.write(b"test file content")

    @classmethod
    def tearDownClass(cls):
        """Cleanup test files."""
        gripsbox_path = os.path.join(cls.APP_STORAGE, "gripsbox")
        test_file_path = os.path.join(gripsbox_path, cls.TEST_FILE)

        # Remove the specific test file
        if os.path.exists(test_file_path):
            os.remove(test_file_path)

        # Optionally, remove other files in gripsbox_path if needed
        for file_name in os.listdir(gripsbox_path):
            file_path = os.path.join(gripsbox_path, file_name)
            if os.path.isfile(file_path):
                os.remove(file_path)

        # Close the session
        cls.session.close()

    def create_test_gripsbox(self):
        """Create a test gripsbox using the model and return its UUID."""
        # Create the payload with GripsboxPostRequestModel
        gripsbox_data = GripsboxPostRequestModel(
            name="Test Grip",
            size=5,
            type="Type Y",
            active=True,
            tags=["tag1", "tag2"]
        )

        # Convert the model to a dictionary and ensure all UUIDs are strings
        payload_dict = gripsbox_data.dict()

        # Prepare files for the POST request
        with open(self.TEST_FILE, "rb") as file:
            files = {"file": (self.TEST_FILE, file, "text/plain")}
            headers = {"X-API-Key": self.api_key}
            response = requests.post(
                f"{self.BASE_URL}/gripsbox",
                files=files,
                data=payload_dict,
                headers=headers
            )

        if response.status_code != 201:
            self.fail(f"Failed to create gripsbox: {response.text}")

        # Return the ID of the newly created gripsbox
        return response.json().get('id')

    def test_create_and_delete_gripsbox(self):
        """Test creating a new gripsbox and deleting it."""
        # Create a new test gripsbox
        new_id = self.create_test_gripsbox()

        # Validate gripsbox creation by checking if it appears in the list of gripsboxes
        headers = {"X-API-Key": self.api_key}
        response = requests.get(f"{self.BASE_URL}/gripsbox", headers=headers)
        if response.status_code != 200:
            self.fail(f"Failed to get gripsboxes after creation: {response.text}")
        gripsboxes = response.json()
        self.assertTrue(any(gripsbox['id'] == new_id for gripsbox in gripsboxes), "Gripsbox not found after creation")

        # Delete the newly created gripsbox
        self.delete_gripsbox(new_id)

        # Validate gripsbox deletion by checking if it's removed from the list
        response = requests.get(f"{self.BASE_URL}/gripsbox", headers=headers)
        if response.status_code != 200:
            self.fail(f"Failed to get gripsboxes after deletion: {response.text}")
        gripsboxes = response.json()
        self.assertFalse(any(gripsbox['id'] == new_id for gripsbox in gripsboxes),
                         "Gripsbox still found after deletion")

    def delete_gripsbox(self, gripsbox_id):
        """Delete the given gripsbox by UUID."""
        headers = {"X-API-Key": self.api_key}
        delete_response = requests.delete(f"{self.BASE_URL}/gripsbox/{gripsbox_id}", headers=headers)
        if delete_response.status_code != 200:
            self.fail(f"Failed to delete gripsbox: {delete_response.text}")
        delete_data = delete_response.json()
        if delete_data.get('status') != "Gripsbox deleted successfully":
            self.fail(f"Unexpected response for gripsbox deletion: {delete_data}")


if __name__ == '__main__':
    unittest.main()
