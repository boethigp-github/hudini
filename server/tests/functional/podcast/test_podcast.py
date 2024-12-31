import asyncio
import os
import requests
import json
from server.app.config.settings import Settings
from server.app.models.gripsbox.gripsbox_post_request import GripsboxPostRequestModel
from server.tests.test_abstract import TestAbstract
import pytest


class TestPodcast(TestAbstract):
    @classmethod
    def setUpClass(cls):
        """Setup Test Environment."""
        cls.settings = Settings()
        cls.BASE_URL = cls.settings.get("default").get("SERVER_URL")
        cls.APP_STORAGE = cls.settings.get("default").get("APP_STORAGE")
        cls.APP_DEFAULT_ADMIN_USERNAME = "pboethig"

        # Manually run async initialization using asyncio.run() to retrieve API key
        asyncio.run(cls.async_init())

        # Nutze das Testfile aus dem Ordner des Tests
        cls.TEST_FILE = os.path.join(os.path.dirname(__file__), "test_file.txt")

        # Stelle sicher, dass die Datei existiert
        if not os.path.exists(cls.TEST_FILE):
            raise FileNotFoundError(f"Testdatei {cls.TEST_FILE} nicht gefunden.")

    def test_create_podcast_gripsbox(self):
        """Testet die Erstellung einer Gripsbox für Podcasts."""
        asyncio.run(self.async_test_podcast_gripsbox())

    async def async_test_podcast_gripsbox(self):
        """Erstellt eine Gripsbox mit einem Podcast."""

        # 1. Gripsbox erstellen
        gripsbox_data = GripsboxPostRequestModel(
            name=self.TEST_FILE,
            size=10,  # 10 MB
            type="text/html",
            active=True,
            tags=["podcast", "test"],
            models=["gpt-3.5-turbo"]
        )

        # Konvertiere das Modell zu Form-Daten
        payload = gripsbox_data.model_dump()
        payload['tags'] = json.dumps(payload['tags'])
        payload['models'] = json.dumps(payload['models'])

        # Datei und Form-Daten an API senden
        with open(self.TEST_FILE, "rb") as f:
            response = requests.post(
                f"{self.BASE_URL}/gripsbox?api_key={self.api_key}",
                files={"file": (self.TEST_FILE, f, "text/html")},  # Content-Type als text/html
                data=payload
            )

        # Prüfen, ob die Gripsbox erstellt wurde
        assert response.status_code == 201, f"Expected 201 but got {response.status_code}. Response: {response.text}"

        # ID und Benutzer-UUID speichern
        response_data = response.json()
        self.__class__.gripsbox_id = response_data.get('id')
        self.__class__.user_uuid = response_data.get('user')

        # 2. Podcast aus Gripsbox erstellen
        podcast_payload = {
            "gripsbox_id": self.gripsbox_id,  # ID der erstellten Gripsbox
            "speakers": ["Anna", "Tom"]  # Optional: Sprecher
        }

        podcast_response = requests.post(
            f"{self.BASE_URL}/podcasts?api_key={self.api_key}",
            json=podcast_payload
        )

        # Prüfen, ob der Podcast erfolgreich erstellt wurde
        assert podcast_response.status_code == 201, f"Expected 201 but got {podcast_response.status_code}. Response: {podcast_response.text}"

        # 3. Podcast validieren
        podcast_data = podcast_response.json()
        assert "id" in podcast_data
        assert "title" in podcast_data
        assert "audio_url" in podcast_data

