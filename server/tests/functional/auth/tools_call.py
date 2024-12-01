import unittest
import requests
from server.app.config.settings import Settings
from server.app.models.tools.tool_call_request_model import ToolCallRequestModel  # Import the correct request model

class TestToolCalls(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Initialize the settings
        cls.settings = Settings()

        # Set the BASE_URL from the loaded configuration
        cls.BASE_URL = cls.settings.get("default").get("SERVER_URL")

    def test_tool_call_get_weather(self):
        # Test a valid tool call for "get_weather"
        payload = ToolCallRequestModel(
            tool="get_weather",
            parameters={"location": "Berlin"}
        ).dict()  # Convert the Pydantic model to a dict for sending as JSON

        response = requests.post(f"{self.BASE_URL}/tools/call", json=payload)
        self.assertEqual(response.status_code, 200)

        result = response.json()
        self.assertEqual(result['tool'], "get_weather")
        self.assertIn("Weather data for Berlin", result['result']['message'])
        self.assertIn("location", result['result']['data'])
        self.assertIn("temperature", result['result']['data'])
        self.assertIn("condition", result['result']['data'])

    def test_tool_call_unknown_tool(self):
        # Test a tool call with an unknown tool name
        payload = ToolCallRequestModel(
            tool="unknown_tool",
            parameters={"param1": "value1"}
        ).dict()  # Convert the Pydantic model to a dict

        response = requests.post(f"{self.BASE_URL}/tools/call", json=payload)
        self.assertEqual(response.status_code, 200)

        result = response.json()
        self.assertEqual(result['tool'], "unknown_tool")
        self.assertIn("No implementation for tool", result['result']['message'])

    def test_tool_call_missing_parameters(self):
        # Test a tool call with missing parameters
        payload = ToolCallRequestModel(
            tool="get_weather",
            parameters={}  # No location provided
        ).dict()  # Convert the Pydantic model to a dict

        response = requests.post(f"{self.BASE_URL}/tools/call", json=payload)
        self.assertEqual(response.status_code, 200)

        result = response.json()
        self.assertEqual(result['tool'], "get_weather")
        self.assertIn("Weather data for unknown", result['result']['message'])  # Defaulting to 'unknown'

if __name__ == '__main__':
    unittest.main()
