import requests
import unittest
from pydantic import ValidationError
from server.app.config.settings import Settings
from server.app.models.models.models_get_response import ModelGetResponseModel
from server.tests.test_abstract import TestAbstract  # Assuming test_abstract.py is in the same directory
import asyncio
class TestModels(TestAbstract):
    """
    A test class for model-related API endpoints.
    This class contains test methods to verify the functionality of the '/models' endpoint,
    ensuring it returns the expected data structure and response code.
    Attributes:
        BASE_URL (str): The base URL for the API server, retrieved from the Settings object.
    """

    @classmethod
    def setUpClass(cls):
        """Synchronous setup, but manually run async initialization."""
        # Initialize the settings
        cls.settings = Settings()
        cls.BASE_URL = cls.settings.get("default").get("SERVER_URL")
        cls.APP_DEFAULT_ADMIN_USERNAME = cls.settings.get("default").get("APP_DEFAULT_ADMIN_USERNAME")

        # Manually run async initialization using asyncio.run()
        asyncio.run(cls.async_init())

    def test_models(self):
        """
        Test the '/models' endpoint.
        This method sends a GET request to the '/models' endpoint
        and verifies that the response status code is 200 (OK) and that
        the data conforms to the expected schema defined by ModelGetResponseModel.
        """
        # Use the API key as a query parameter
        response = requests.get(f"{self.BASE_URL}/models?api_key={self.api_key}")
        self.assertEqual(response.status_code, 200, "Expected response code 200")

        # Attempt to deserialize the JSON response to Pydantic models
        try:
            models = [ModelGetResponseModel(**model) for model in response.json()]
        except ValidationError as e:
            self.fail(f"Response validation failed due to data structure issues: {e}")

if __name__ == '__main__':
    unittest.main()
