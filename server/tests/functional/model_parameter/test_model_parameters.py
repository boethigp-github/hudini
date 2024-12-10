import unittest
import requests
import uuid
from server.app.config.settings import Settings
from server.app.models.model_parameter.models_parameter_request import ModelParameterRequestModel
from server.tests.test_abstract import TestAbstract  # Assuming test_abstract contains API key logic
import asyncio


class TestModelParameters(TestAbstract):
    @classmethod
    def setUpClass(cls):
        """Synchronous setup, including the API key retrieval."""
        cls.settings = Settings()
        cls.BASE_URL = cls.settings.get("default").get("SERVER_URL")
        cls.APP_DEFAULT_ADMIN_USERNAME = "pboethig"

        # Manually run async initialization using asyncio.run() to retrieve API key
        asyncio.run(cls.async_init())

        # Fetch the first user UUID
        cls.TEST_USER_UUID = cls.get_first_user_uuid()

    @classmethod
    def get_first_user_uuid(cls):
        """Fetch the first user from the database."""
        response = requests.get(f"{cls.BASE_URL}/users?api_key={cls.api_key}")
        if response.status_code != 200:
            raise AssertionError(f"Failed to fetch users: {response.text}")

        users = response.json()
        if not users:
            raise AssertionError("No users found in the database")

        return str(users[0]['uuid'])  # Ensure UUID is a string

    def create_test_model_parameter(self):
        """Create a test model parameter."""
        if not self.TEST_USER_UUID:
            raise AssertionError("TEST_USER_UUID is None, cannot create test model parameter")

        # Create the payload
        create_payload = ModelParameterRequestModel(
            user=self.TEST_USER_UUID,
            parameter="max_tokens",
            model="gpt-4",
            value={"max": 1024},
            active=True,
        )

        # Convert the model to a dictionary and ensure UUIDs are strings
        payload_dict = create_payload.model_dump()
        payload_dict['user'] = str(payload_dict['user'])  # Ensure the UUID is serialized as a string

        # Send the POST request with the API key as a query parameter
        create_response = requests.post(f"{self.BASE_URL}/model-parameters?api_key={self.api_key}", json=payload_dict)

        # Check for successful creation
        if create_response.status_code != 201:
            raise AssertionError(f"Failed to create test model parameter: {create_response.text}")

        # Return the UUID of the newly created model parameter
        return create_response.json().get('uuid')

    def test_create_and_delete_model_parameter(self):
        """Test creating a new model parameter and deleting it."""
        # Create a new test model parameter
        new_uuid = self.create_test_model_parameter()

        # Validate model parameter creation by checking if it appears in the list
        response = requests.get(f"{self.BASE_URL}/model-parameters?api_key={self.api_key}")
        if response.status_code != 200:
            raise AssertionError(f"Failed to get model parameters after creation: {response.text}")
        parameters = response.json()
        self.assertTrue(
            any(parameter['uuid'] == new_uuid for parameter in parameters),
            f"Model parameter {new_uuid} not found after creation: {parameters}"
        )

        # Delete the newly created model parameter
        self.delete_model_parameter(new_uuid)

        # Validate model parameter deletion by checking if it's removed from the list
        response = requests.get(f"{self.BASE_URL}/model-parameters?api_key={self.api_key}")
        if response.status_code != 200:
            raise AssertionError(f"Failed to get model parameters after deletion: {response.text}")
        parameters = response.json()
        self.assertFalse(
            any(parameter['uuid'] == new_uuid for parameter in parameters),
            "Model parameter still found after deletion"
        )

    def test_get_model_parameters_by_user(self):
        """Test retrieving model parameters for a specific user."""
        # Create a new test model parameter for the user
        new_uuid = self.create_test_model_parameter()

        # Fetch model parameters for the specific user
        response = requests.get(f"{self.BASE_URL}/model-parameters/user?api_key={self.api_key}")
        if response.status_code != 200:
            raise AssertionError(f"Failed to get model parameters for user: {response.text}")

        parameters = response.json()

        # Validate that the created model parameter appears in the user's parameters
        self.assertTrue(
            any(parameter['uuid'] == new_uuid for parameter in parameters),
            f"Model parameter {new_uuid} not found in user's parameters: {parameters}"
        )

        # Clean up by deleting the created model parameter
        self.delete_model_parameter(new_uuid)

    def delete_model_parameter(self, parameter_id):
        """Delete the given model parameter by UUID."""
        delete_response = requests.delete(f"{self.BASE_URL}/model-parameters/{parameter_id}?api_key={self.api_key}")
        if delete_response.status_code != 200:
            raise AssertionError(f"Failed to delete model parameter: {parameter_id}: {delete_response.text}")
        delete_data = delete_response.json()
        if delete_data.get('status') != "Model parameter deleted successfully":
            raise AssertionError(f"Unexpected response for model parameter deletion: {delete_data}")


if __name__ == '__main__':
    unittest.main()
