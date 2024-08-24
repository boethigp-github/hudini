import unittest
import requests
import yaml
import os

class TestSwagger(unittest.TestCase):
    BASE_URL = os.getenv('SERVER_URL', 'http://localhost:5000')

    def test_swagger_yaml(self):
        response = requests.get(f"{self.BASE_URL}/swagger.yaml")
        self.assertEqual(200, response.status_code)
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

    def test_swagger_ui(self):
        response = requests.get(f"{self.BASE_URL}/api/docs")
        self.assertEqual(200, response.status_code)
        self.assertIn('text/html', response.headers['Content-Type'])

        # Verify that the Swagger UI HTML is served
        self.assertIn('<html', response.text.lower())
        self.assertIn('swagger', response.text.lower())
        self.assertIn('swagger-ui', response.text.lower())

if __name__ == '__main__':
    unittest.main()
