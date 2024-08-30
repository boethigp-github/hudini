import unittest
import requests
import json
import uuid
from server.app.config.settings import Settings  # Passe den Import entsprechend deiner Projektstruktur an

class TestGenerateAndStream(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # Initialisiere die Einstellungen
        cls.settings = Settings()

        # Setze die SERVER_URL aus der geladenen Konfiguration
        cls.SERVER_URL = cls.settings.get("default").get("SERVER_URL")

    def test_stream_success(self):
        """Teste den /stream-Endpunkt für eine erfolgreiche Streaming-Antwort."""
        stream_payload = {
            "models": [
                {
                    "category": "text_completion",
                    "description": "A language model for text completions",
                    "id": "gpt-3.5-turbo",
                    "max_tokens": 100,
                    "model": "gpt-3.5-turbo",
                    "object": "chat.completion",
                    "platform": "openai",
                    "temperature": 0.7
                }
            ],
            "prompt": "Write a rant in the style of Linus Torvalds about using spaces instead of tabs for indentation in code.",
            "prompt_id": "550e8400-e29b-41d4-a716-446655440000",  # Feste prompt_id aus den Testdaten
            "method_name": "fetch_completion"
        }
        response = requests.post(f"{self.SERVER_URL}/stream", json=stream_payload, stream=True, timeout=10)
        self.assertEqual(response.status_code, 200)  # Erwarte 200 OK
        self.assertEqual(response.headers['Content-Type'], 'application/json')

        buffer = ""
        for i, line in enumerate(response.iter_lines()):
            if line:
                buffer += line.decode('utf-8')
                try:
                    event_data = json.loads(buffer)
                    self.assertIn("model", event_data)
                    self.assertIn("completion", event_data)
                    buffer = ""
                except json.JSONDecodeError:
                    continue

            if i >= 50:  # Begrenze die Anzahl der empfangenen Zeilen
                break

    def test_stream_bad_request(self):
        """Teste den /stream-Endpunkt für eine fehlerhafte Anfrage."""
        stream_payload = {
            "prompt": "Tell me a short joke"
            # Absichtlich das "models"-Feld weggelassen
        }
        response = requests.post(f"{self.SERVER_URL}/stream", json=stream_payload)
        self.assertEqual(response.status_code, 422)

    def test_stream_invalid_model(self):
        """Teste den /stream-Endpunkt mit einem ungültigen Modell."""
        stream_payload = {
            "models": [
                {
                    "category": "text_completion",
                    "description": "Invalid model for testing",
                    "id": "invalid-model",
                    "max_tokens": 100,
                    "model": "invalid-model",
                    "object": "model",
                    "platform": "unknown",  # Ungültige Plattform
                    "temperature": 0.7
                }
            ],
            "prompt": "This is a test",
            "prompt_id": str(uuid.uuid4()),
            "method_name": "fetch_completion"
        }
        response = requests.post(f"{self.SERVER_URL}/stream", json=stream_payload)
        self.assertEqual(response.status_code, 422)  # Erwarte 422 Unprocessable Entity

    def test_stream_unsupported_platform(self):
        """Teste den /stream-Endpunkt mit einer nicht unterstützten Plattform."""
        stream_payload = {
            "models": [
                {
                    "category": "text_completion",
                    "description": "Model on unsupported platform",
                    "id": "some-model",
                    "max_tokens": 100,
                    "model": "some-model",
                    "object": "model",
                    "platform": "unsupported_platform",  # Nicht unterstützte Plattform
                    "temperature": 0.7
                }
            ],
            "prompt": "This is a test",
            "prompt_id": str(uuid.uuid4()),
            "method_name": "fetch_completion"
        }
        response = requests.post(f"{self.SERVER_URL}/stream", json=stream_payload)
        self.assertEqual(response.status_code, 422)  # Erwarte 422 Unprocessable Entity

if __name__ == '__main__':
    unittest.main()
