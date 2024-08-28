import requests
import unittest
from server.app.config.settings import Settings  # Adjust the import according to your project structure

class TestModels(unittest.TestCase):
    """
    A test class for model-related API endpoints.

    This class contains test methods to verify the functionality
    of the '/models' endpoint, ensuring it returns the expected
    data structure and response code.

    Attributes:
        BASE_URL (str): The base URL for the API server, retrieved from
                        the Settings object.
    """

    @classmethod
    def setUpClass(cls):
        # Initialize the settings
        cls.settings = Settings()

        # Set the BASE_URL from the loaded configuration
        cls.BASE_URL = cls.settings.get("default").get("SERVER_URL");

    def test_models(self):
        """
        Test the '/models' endpoint.

        This method sends a GET request to the '/models' endpoint
        and verifies that:
        1. The response status code is 200 (OK).
        2. The response JSON contains 'models' keys.

        5. The 'category' key in each model is not null and is a string.

        Raises:
            AssertionError: If any of the assertions fail.
        """
        response = requests.get(f"{self.BASE_URL}/models")
        assert response.status_code == 200
        data = response.json()

        for model in data:
            assert 'id' in model, "Model should have an 'id' field"
            assert 'object' in model, "Model should have an 'object' field"
            assert 'created' in model, "Model should have a 'created' field"
            assert 'owned_by' in model, "Model should have an 'owned_by' field"
            assert 'category' in model, "Model should have a 'category' field"
            assert 'platform' in model, "Model should have a 'platform' field"
            assert isinstance(model['category'], str), "Model 'category' should be a string"
            assert model['category'] is not None, "Model 'category' should not be null"
            assert 'description' in model, "Model should have a 'description' field"
            assert isinstance(model['description'], str) or model['description'] is None, "Model 'description' should be a string or None"

if __name__ == '__main__':
    unittest.main()
