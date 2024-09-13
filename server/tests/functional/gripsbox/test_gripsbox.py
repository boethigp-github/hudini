import unittest
import requests
import os
from server.app.config.settings import Settings
from server.app.models.gripsbox.gripsbox_post_request import GripsboxPostRequestModel


class TestGripsbox(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.settings = Settings()
        cls.BASE_URL = cls.settings.get("default").get("SERVER_URL")
        cls.APP_STORAGE = cls.settings.get("default").get("APP_STORAGE")
        cls.TEST_FILE = "test_file.txt"
        cls.create_test_file()

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
            response = requests.post(
                f"{self.BASE_URL}/gripsbox",
                files=files,
                data=payload_dict
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
        response = requests.get(f"{self.BASE_URL}/gripsbox")
        if response.status_code != 200:
            self.fail(f"Failed to get gripsboxes after creation: {response.text}")
        gripsboxes = response.json()
        self.assertTrue(any(gripsbox['id'] == new_id for gripsbox in gripsboxes), "Gripsbox not found after creation")

        # Delete the newly created gripsbox
        self.delete_gripsbox(new_id)

        # Validate gripsbox deletion by checking if it's removed from the list
        response = requests.get(f"{self.BASE_URL}/gripsbox")
        if response.status_code != 200:
            self.fail(f"Failed to get gripsboxes after deletion: {response.text}")
        gripsboxes = response.json()
        self.assertFalse(any(gripsbox['id'] == new_id for gripsbox in gripsboxes),
                         "Gripsbox still found after deletion")

    def delete_gripsbox(self, gripsbox_id):
        """Delete the given gripsbox by UUID."""
        delete_response = requests.delete(f"{self.BASE_URL}/gripsbox/{gripsbox_id}")
        if delete_response.status_code != 200:
            self.fail(f"Failed to delete gripsbox: {delete_response.text}")
        delete_data = delete_response.json()
        if delete_data.get('status') != "Gripsbox deleted successfully":
            self.fail(f"Unexpected response for gripsbox deletion: {delete_data}")


if __name__ == '__main__':
    unittest.main()
