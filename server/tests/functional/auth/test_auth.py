import unittest
import requests
import os
from server.app.config.settings import Settings


class TestOAuthRouter(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.settings = Settings()
        cls.BASE_URL = cls.settings.get("default").get("SERVER_URL")
        cls.google_client_id = cls.settings.get("default").get("APP_GOOGLE_AUTH_CLIENT_ID")
        cls.google_client_secret = cls.settings.get("default").get("APP_GOOGLE_AUTH_CLIENT_SECRET")
        cls.google_redirect_uri = cls.settings.get("default").get("APP_GOOGLE_AUTH_REDIRECT_URI")

        if not all([cls.google_client_id, cls.google_client_secret, cls.google_redirect_uri]):
            raise ValueError("Missing Google OAuth configuration settings")

    def test_login_google(self):
        """Test Google OAuth login endpoint."""
        response = requests.get(f"{self.BASE_URL}/auth/login/google")
        # Ensure that the response redirects to Google's OAuth URL
        self.assertEqual(response.status_code, 200)

    def test_no_active_session(self):
        """Test session-info route when there is no active session."""
        response = requests.get(f"{self.BASE_URL}/auth/session-info")

        # Expecting a 401 Unauthorized response
        self.assertEqual(response.status_code, 401)

        # Checking if the response contains the expected error message
        self.assertEqual(response.content, b'{"detail":"No active session found"}')


if __name__ == '__main__':
    unittest.main()
