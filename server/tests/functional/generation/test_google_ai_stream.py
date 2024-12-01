import unittest
import requests
import uuid
from server.app.config.settings import Settings
import json
import asyncio
from server.tests.test_abstract import TestAbstract  # Assuming this contains the API key logic

class TestGoogleAIStream(TestAbstract):

    @classmethod
    def setUpClass(cls):
        # Lade die Einstellungen über die Settings-Klasse
        cls.settings = Settings()

        # Setze die SERVER_URL und APP_DEFAULT_ADMIN_USERNAME aus den geladenen Konfigurationen
        cls.SERVER_URL = cls.settings.get("default").get("SERVER_URL")
        cls.APP_DEFAULT_ADMIN_USERNAME = cls.settings.get("default").get("APP_DEFAULT_ADMIN_USERNAME")

        # Manually run async initialization using asyncio.run() to retrieve API key
        asyncio.run(cls.async_init())

    def test_stream_google_ai_success(self):
        """Test des /stream/google-ai Endpunkts für eine erfolgreiche Antwort mittels eines Google AI Modells."""
        stream_payload = {
            "id": str(uuid.uuid4()),  # Generiere eine eindeutige ID für die Anfrage
            "prompt": "Erzähl mir einen kurzen Witz",
            "models": [{
                "category": "text_completion",
                "created": 1712361441,
                "description": "Modell gemini-1.5-flash kategorisiert als text_completion, verfügbar bei Google AI",
                "id": str(uuid.uuid4()),
                "model": "gemini-1.5-flash",
                "object": "model",
                "owned_by": "google",
                "parent": None,
                "permission": None,
                "platform": "google_ai",
                "root": None,
                "temperature": 0.7,
                "top_p": 0.9,
                "top_k": 50,
                "max_tokens": 100
            }]
        }

        # Sende die Anfrage und streame die Antwort unter Verwendung des Admin API-Schlüssels
        response = requests.post(f"{self.SERVER_URL}/stream/google-ai?api_key={self.api_key}", json=stream_payload, stream=True, timeout=20)

        # Überprüfe den Statuscode und den Content-Type der Antwort
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers['Content-Type'], 'application/json')

        buffer = ""
        for line in response.iter_lines():
            if line:
                buffer += line.decode('utf-8')
                try:
                    event_data = json.loads(buffer)
                    self.assertIn("model", event_data)
                    self.assertIn("completion", event_data)
                    buffer = ""
                except json.JSONDecodeError:
                    continue

    def test_stream_google_ai_invalid_model(self):
        """Test des /stream/google-ai Endpunkts mit einem ungültigen Google AI Modell."""
        stream_payload = {
            "id": str(uuid.uuid4()),  # Generiere eine eindeutige ID für die Anfrage
            "prompt": "Das ist ein Test",
            "models": [{
                "category": "text_completion",
                "created": 1712361441,
                "description": "Ungültiges Modell zum Testen",
                "id": "invalid-google-model",
                "model": "invalid-google-model",
                "object": "model",
                "owned_by": "google",
                "parent": None,
                "permission": None,
                "platform": "google_ai",
                "root": None
            }]
        }

        # Sende die Anfrage unter Verwendung des Admin API-Schlüssels
        response = requests.post(f"{self.SERVER_URL}/stream/google-ai?api_key={self.api_key}", json=stream_payload, stream=True)

        # Hier wird erwartet, dass der Statuscode 200 ist, weil das Modell ungültig ist
        self.assertEqual(response.status_code, 200)


if __name__ == '__main__':
    unittest.main()
