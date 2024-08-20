import unittest
import requests
import yaml
import os
from dotenv import load_dotenv

# Get the current file's directory
current_dir = os.path.dirname(os.path.abspath(__file__))

# Construct the path to .env.local
env_path = os.path.join(current_dir, '..', '..', '.env.local')

# Load environment variables from .env.local
load_dotenv(env_path)

class TestSwagger(unittest.TestCase):
    BASE_URL = os.getenv('SERVER_URL', 'http://localhost:5000')

    def test_swagger_yaml(self):
        response = requests.get(f"{self.BASE_URL}/swagger.yaml")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers['Content-Type'], 'application/x-yaml')

        # Parse the YAML content
        try:
            swagger_data = yaml.safe_load(response.text)
        except yaml.YAMLError as e:
            self.fail(f"Failed to parse YAML: {e}")

        # Check for essential Swagger/OpenAPI elements
        self.assertIn('openapi', swagger_data)
        self.assertIn('info', swagger_data)
        self.assertIn('paths', swagger_data)

        # Check if there's at least one endpoint defined
        self.assertTrue(len(swagger_data['paths']) > 0, "No endpoints defined in Swagger YAML")

if __name__ == '__main__':
    unittest.main()
