import unittest
import requests
from server.app.config.settings import Settings
from server.app.models.tools.tool_call_request_model import ToolCallRequestModel  # Import the correct request model
from server.tests.test_abstract import TestAbstract
import asyncio

class TestToolCalls(TestAbstract):
    @classmethod
    def setUpClass(cls):
        """Synchronous setup, including the API key retrieval and admin user details."""
        cls.settings = Settings()
        cls.BASE_URL = cls.settings.get("default").get("SERVER_URL")
        cls.APP_DEFAULT_ADMIN_USERNAME = cls.settings.get("default").get("APP_DEFAULT_ADMIN_USERNAME")

        # Manually run async initialization using asyncio.run() to retrieve API key
        asyncio.run(cls.async_init())

    def test_tool_call_get_weather(self):
        """Test a valid tool call for 'get_weather'."""
        payload = ToolCallRequestModel(
            tool="get_weather",
            parameters={"location": "Berlin"}
        ).model_dump()  # Convert the Pydantic model to a dict for sending as JSON

        # Send POST request with the API key in the URL
        response = requests.post(f"{self.BASE_URL}/tools/call?api_key={self.api_key}", json=payload)
        self.assertEqual(response.status_code, 200)

        result = response.json()
        self.assertEqual(result['tool'], "get_weather")
        self.assertIn("Weather data for Berlin", result['result']['message'])
        self.assertIn("location", result['result']['data'])
        self.assertIn("temperature", result['result']['data'])
        self.assertIn("condition", result['result']['data'])

    def test_tool_call_unknown_tool(self):
        """Test a tool call with an unknown tool name."""
        payload = ToolCallRequestModel(
            tool="unknown_tool",
            parameters={"param1": "value1"}
        ).model_dump()  # Convert the Pydantic model to a dict

        # Send POST request with the API key in the URL
        response = requests.post(f"{self.BASE_URL}/tools/call?api_key={self.api_key}", json=payload)
        self.assertEqual(response.status_code, 200)

        result = response.json()
        self.assertEqual(result['tool'], "unknown_tool")
        self.assertIn("No implementation for tool", result['result']['message'])

    def test_tool_call_missing_parameters(self):
        """Test a tool call with missing parameters."""
        payload = ToolCallRequestModel(
            tool="get_weather",
            parameters={}  # No location provided
        ).model_dump()  # Convert the Pydantic model to a dict

        # Send POST request with the API key in the URL
        response = requests.post(f"{self.BASE_URL}/tools/call?api_key={self.api_key}", json=payload)
        self.assertEqual(response.status_code, 200)

        result = response.json()
        self.assertEqual(result['tool'], "get_weather")
        self.assertIn("Weather data for unknown", result['result']['message'])  # Defaulting to 'unknown'

if __name__ == '__main__':
    unittest.main()
