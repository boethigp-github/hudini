import os
import logging
from uuid import uuid4
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field
import openai
import re
from server.app.config.settings import Settings
from server.app.services.gripsbox_service import load_gripsbox_by_id
from server.app.models.podcasts.podcast_response_model import PodcastPostResponseModel

# Logging konfigurieren
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# API-Router erstellen
router = APIRouter()

# Settings laden
settings = Settings()

# Speicherpfad für Podcasts
STORAGE_PATH = settings.get("default").get("APP_STORAGE")
PODCAST_STORAGE_PATH = os.path.join(STORAGE_PATH, "audio", "podcasts")

# Sicherstellen, dass das Speicherverzeichnis existiert
os.makedirs(PODCAST_STORAGE_PATH, exist_ok=True)

# OpenAI API-Key aus Settings laden
openai.api_key = settings.get("default").get("API_KEY_OPEN_AI")


# Request Model für den Podcast
class PodcastGripsboxRequestModel(BaseModel):
    gripsbox_id: str = Field(..., description="Gripsbox ID")
    speakers: list = Field(default=["Anna", "Tom"], description="Liste der Sprecher")


def split_text_into_chunks(text: str, max_length: int = 4096):
    """
    Splits the input text into chunks that do not exceed the max_length.
    """
    return [text[i:i + max_length] for i in range(0, len(text), max_length)]


@router.post("/podcasts", response_model=PodcastPostResponseModel, status_code=status.HTTP_201_CREATED)
async def create_podcast(
    gripsbox_data: PodcastGripsboxRequestModel
):
    """
    Erstellt einen Podcast aus einer Gripsbox mit Textinhalt über die OpenAI TTS-API.
    """
    gripsbox_id = gripsbox_data.gripsbox_id
    speakers = gripsbox_data.speakers
    logger.debug(f"Request erhalten - Gripsbox ID: {gripsbox_id}, Sprecher: {speakers}")

    # 1. Gripsbox-Inhalt abrufen
    try:
        text = await load_gripsbox_by_id(gripsbox_id)
    except HTTPException as e:
        raise e

    # 2. Text verarbeiten und validieren
    if isinstance(text, list):  # Falls der Text eine Liste ist, konvertiere ihn
        text = " ".join(text)

    # Sonderzeichen und mehrfache Leerzeichen entfernen
    text = re.sub(r'\s+', ' ', text).strip()

    # Text validieren
    if not isinstance(text, str) or len(text) == 0:
        logger.error(f"Gripsbox enthält keinen gültigen Text für den Podcast.")
        raise HTTPException(status_code=400, detail="Gripsbox enthält keinen Text.")

    logger.debug(f"Geladener Text nach Verarbeitung: {text[:200]}...")

    # 3. Text in Blöcke teilen
    text_chunks = split_text_into_chunks(text)

    # 4. OpenAI TTS-Client verwenden
    try:
        audio_content = b""  # MP3-Dateien zusammenfügen
        voices = ["alloy", "nova", "echo"]  # Verschiedene Stimmen

        # Textblöcke an die TTS-API senden
        for i, chunk in enumerate(text_chunks):
            if len(chunk) > 4096:
                logger.warning(f"Chunk {i+1} überschreitet 4096 Zeichen: {len(chunk)}")
                continue

            # Stimme auswählen
            voice = voices[i % len(voices)]

            # **Neue OpenAI-TTS-API aufrufen**
            response = openai.audio.speech.create(
                model="tts-1",
                input=chunk,
                voice=voice,
                response_format="mp3"
            )

            # Überprüfen, ob die Antwort gültig ist
            if not response or not hasattr(response, 'content'):
                logger.error("Leere Antwort von der TTS-API erhalten.")
                raise HTTPException(status_code=500, detail="Leere Antwort von der TTS-API.")

            # MP3-Inhalt hinzufügen
            audio_content += response.content

    except Exception as e:
        logger.error(f"TTS-API-Fehler: {str(e)}")
        raise HTTPException(status_code=500, detail=f"TTS-API-Fehler: {str(e)}")

    # 5. Audio speichern
    podcast_id = str(uuid4())  # Eindeutige ID generieren
    file_name = f"{podcast_id}.mp3"
    file_path = os.path.join(PODCAST_STORAGE_PATH, file_name)

    try:
        with open(file_path, "wb") as audio_file:
            audio_file.write(audio_content)

        logger.info(f"Podcast gespeichert unter: {file_path}")
    except PermissionError:
        logger.error(f"Keine Schreibrechte für: {file_path}")
        raise HTTPException(status_code=500, detail="Keine Schreibrechte für das Verzeichnis.")
    except Exception as e:
        logger.error(f"Fehler beim Speichern der MP3-Datei: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Fehler beim Speichern der Datei: {str(e)}")

    # 6. URL erstellen und Response zurückgeben
    audio_url = f"/static/audio/podcasts/{file_name}"
    return PodcastPostResponseModel(id=podcast_id, title="Gripsbox Podcast", audio_url=audio_url)
