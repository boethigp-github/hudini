import os
import logging
from uuid import uuid4
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field
import re
from google.cloud import texttospeech
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

# Google API-Key aus den Settings laden
GOOGLE_API_KEY = settings.get("default").get("APP_GOOGLE_CLOUD_API_KEY")


# Request Model für den Podcast
class PodcastGripsboxRequestModel(BaseModel):
    gripsbox_id: str = Field(..., description="Gripsbox ID")
    speakers: list = Field(default=["Anna", "Tom"], description="Liste der Sprecher")


def split_text_into_chunks(text: str, max_bytes: int = 4000):
    """
    Teilt den Text in Blöcke, die maximal 4000 Bytes lang sind.
    """
    chunks = []
    current_chunk = ""
    for word in text.split():
        if len((current_chunk + " " + word).encode('utf-8')) > max_bytes:
            chunks.append(current_chunk.strip())
            current_chunk = word
        else:
            current_chunk += " " + word
    chunks.append(current_chunk.strip())
    return chunks


def synthesize_google_speech(text_chunks: list, voice_name: str, language_code: str = "de-DE"):
    """
    Erstellt Sprache aus Textblöcken mit der Google TTS-API.
    """
    client = texttospeech.TextToSpeechClient(client_options={"api_key": GOOGLE_API_KEY})
    audio_content = b""

    for i, chunk in enumerate(text_chunks):
        logger.debug(f"Verarbeite Chunk {i+1}/{len(text_chunks)}: {chunk[:50]}...")

        # Eingabetext konfigurieren
        input_text = texttospeech.SynthesisInput(text=chunk)

        # Stimme festlegen
        voice = texttospeech.VoiceSelectionParams(
            language_code=language_code,
            name=voice_name,
            ssml_gender=texttospeech.SsmlVoiceGender.NEUTRAL
        )

        # Audio-Format festlegen
        audio_config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.MP3
        )

        try:
            # API-Aufruf
            response = client.synthesize_speech(
                input=input_text,
                voice=voice,
                audio_config=audio_config
            )
            audio_content += response.audio_content  # Audio-Bytes hinzufügen

        except Exception as e:
            logger.error(f"Google API Fehler bei Chunk {i+1}: {str(e)}")
            raise HTTPException(status_code=500, detail=f"API-Fehler: {str(e)}")

    return audio_content


@router.post("/podcasts", response_model=PodcastPostResponseModel, status_code=status.HTTP_201_CREATED)
async def create_podcast(gripsbox_data: PodcastGripsboxRequestModel):
    """
    Erstellt einen Podcast aus einer Gripsbox mit Textinhalt über die Google TTS-API.
    """
    gripsbox_id = gripsbox_data.gripsbox_id
    speakers = gripsbox_data.speakers
    logger.debug(f"Request erhalten - Gripsbox ID: {gripsbox_id}, Sprecher: {speakers}")

    # 1. Gripsbox-Inhalt abrufen
    try:
        text = await load_gripsbox_by_id(gripsbox_id)
        if isinstance(text, list):
            text = " ".join(text)
    except HTTPException as e:
        raise e

    if not text:
        logger.error("Gripsbox enthält keinen gültigen Text.")
        raise HTTPException(status_code=400, detail="Gripsbox enthält keinen Text.")

    # 2. Deutsche Stimmen definieren
    voice_map = {"Anna": "de-DE-Wavenet-C", "Tom": "de-DE-Wavenet-B"}  # Stimmen

    # 3. Text in Dialoge aufteilen und Namen entfernen!
    sentences = re.split(r'(?<=[.!?])\s+', text)
    dialog = []
    for sentence in sentences:
        # Entferne die Namen (Anna:, Tom:)
        cleaned_sentence = re.sub(r'^(Anna:|Tom:)\s*', '', sentence).strip()
        dialog.append(cleaned_sentence)  # Nur den Text speichern

    # 4. Audio generieren
    audio_content = b""
    for i, sentence in enumerate(dialog):
        # Sprecher abwechselnd zuweisen
        speaker = speakers[i % len(speakers)]
        voice = voice_map[speaker]

        # Satz in Chunks aufteilen
        text_chunks = split_text_into_chunks(sentence)

        # Audio erzeugen
        chunk_audio = synthesize_google_speech(text_chunks, voice)
        audio_content += chunk_audio

    # 5. Datei speichern
    podcast_id = str(uuid4())
    file_name = f"{podcast_id}.mp3"
    file_path = os.path.join(PODCAST_STORAGE_PATH, file_name)

    with open(file_path, "wb") as audio_file:
        audio_file.write(audio_content)

    return PodcastPostResponseModel(id=podcast_id, title="Gripsbox Podcast", audio_url=file_path)
