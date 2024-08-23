import requests
import os
import unittest


class TestModels(unittest.TestCase):
    """
    A test class for model-related API endpoints.

    This class contains test methods to verify the functionality
    of the '/get_models' endpoint, ensuring it returns the expected
    data structure and response code.

    Attributes:
        BASE_URL (str): The base URL for the API server, defaulting to
                        'http://localhost:5000' if SERVER_URL environment
                        variable is not set.
    """

    BASE_URL = os.getenv('SERVER_URL', 'http://localhost:5000')

    def test_get_models(self):
        """
        Test the '/get_models' endpoint.

        This method sends a GET request to the '/get_models' endpoint
        and verifies that:
        1. The response status code is 200 (OK).
        2. The response JSON contains 'local_models' and 'openai_models' keys.
        3. Both 'local_models' and 'openai_models' are lists.

        Raises:
            AssertionError: If any of the assertions fail.
        """
        response = requests.get(f"{self.BASE_URL}/get_models")
        assert response.status_code == 200
        data = response.json()
        assert 'local_models' in data
        assert 'openai_models' in data
        assert isinstance(data['local_models'], list)
        assert isinstance(data['openai_models'], list)