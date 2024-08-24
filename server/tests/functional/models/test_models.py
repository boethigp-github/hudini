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
        4. Each item in 'openai_models' has the expected structure including 'category'.
        5. The 'category' key in each model is not null and is a string.

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

        for model in data['openai_models']:
            assert 'id' in model, "Model should have an 'id' field"
            assert 'object' in model, "Model should have an 'object' field"
            assert 'created' in model, "Model should have a 'created' field"
            assert 'owned_by' in model, "Model should have an 'owned_by' field"
            assert 'category' in model, "Model should have a 'category' field"
            assert isinstance(model['category'], str), "Model 'category' should be a string"
            assert model['category'] is not None, "Model 'category' should not be null"
            assert 'description' in model, "Model should have a 'description' field"
            assert isinstance(model['description'], str) or model['description'] is None, "Model 'description' should be a string or None"

if __name__ == '__main__':
    unittest.main()
