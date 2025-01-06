import os
import logging
import json
import requests
from uuid import uuid4
from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel, Field
from server.app.config.settings import Settings
from server.app.services.gripsbox_service import load_gripsbox_by_id
from server.app.models.podcasts.podcast_response_model import PodcastPostResponseModel
from openai import OpenAI
from server.app.utils.auth import auth
from pydub import AudioSegment

# Logging konfigurieren
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# API-Router erstellen
router = APIRouter()

# Settings laden
settings = Settings()

# API-Schlüssel und URLs
ELEVENLABS_API_KEY = settings.get("default").get("API_KEY_ELEVENLABS")
OPENAI_API_KEY = settings.get("default").get("API_KEY_OPEN_AI")
url = "https://api.elevenlabs.io/v1/text-to-speech"

# Stimmenzuordnung für ElevenLabs
voice_map = {"Anna": "IKne3meq5aSn9XLyUdCD", "Tom": "nPczCjzI2devNBz1zQrb"}


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


def create_audio_save_path(user_uuid: str, gripsbox_uuid: str) -> str:
    """
    Erstellt den Speicherpfad basierend auf user_uuid und gripsbox_uuid.
    """
    # Basis-Pfad für das Speichern von Podcasts
    podcast_storage_path = "C:/projects/houdini/server/storage/audio/podcasts"

    # Sicherstellen, dass der Ordner existiert
    user_gripsbox_path = os.path.join(podcast_storage_path, user_uuid, gripsbox_uuid)
    os.makedirs(user_gripsbox_path, exist_ok=True)

    return user_gripsbox_path


def create_elevenlabs_audio(dialogue: list, user_uuid: str, gripsbox_uuid: str):
    """
    Erstellt Audiodateien für jeden Sprecher und speichert sie im entsprechenden Ordner.
    """
    headers = {
        "Content-Type": "application/json",
        "xi-api-key": ELEVENLABS_API_KEY
    }

    audio_file_paths = []
    user_gripsbox_path = create_audio_save_path(user_uuid, gripsbox_uuid)

    for index, line in enumerate(dialogue):
        payload = {
            "model_id": "eleven_multilingual_v1",
            "text": line["text"],
            "voice_settings": {
                "stability": 0.75,
                "similarity_boost": 0.85
            }
        }

        # API-Request an ElevenLabs senden
        response = requests.post(f"{url}/{line['voice_id']}", headers=headers, json=payload)

        if response.status_code == 200:
            # Dateiname enthält Index und Sprechername
            speaker_name = line.get("speaker", "unknown")
            file_name = f"output_{index:02d}_{speaker_name}.mp3"  # Reihenfolge sichern
            file_path = os.path.join(user_gripsbox_path, file_name)

            with open(file_path, "wb") as audio_file:
                audio_file.write(response.content)

            audio_file_paths.append(file_path)
            logger.debug(f"Audio erfolgreich erstellt: {file_path}")
        else:
            logger.error(f"Fehler {response.status_code} - {response.text}")
            raise HTTPException(status_code=response.status_code, detail=response.text)

    # Reihenfolge sicherstellen (falls Dateinamen anders sortiert werden)
    audio_file_paths.sort()  # Dateien nach Namen sortieren
    return audio_file_paths


def generate_dialog_with_gpt4(text: str):
    """
    Nutzt GPT-4, um den Text in Dialogform zu konvertieren.
    """
    try:
        client = OpenAI(api_key=OPENAI_API_KEY)

        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{
                "role": "system",
                "content": (
                    "Du bist ein Dialog-Generator. "
                    "Teile den gegebenen Text in einen natürlichen Dialog zwischen zwei Sprechern auf. "
                    "Nutze abwechselnd die Namen 'Anna' und 'Tom' und erzeuge realistische Konversationen."
                )
            },
                {"role": "user", "content": text}],
            temperature=0.7,
            max_tokens=2000,
        )
        dialog = response.choices[0].message.content
        return dialog
    except Exception as e:
        logger.error(f"OpenAI API-Fehler: {str(e)}")
        raise HTTPException(status_code=500, detail=f"OpenAI API-Fehler: {str(e)}")


def split_dialog_by_speakers(dialog_text: str, speakers: list):
    """
    Teilt den Dialog basierend auf den Sprechern in Abschnitte auf.
    """
    dialog_parts = []
    current_speaker = None
    current_text = ""

    for line in dialog_text.splitlines():
        if any(line.startswith(f"{speaker}:") for speaker in speakers):
            if current_speaker:
                dialog_parts.append({"speaker": current_speaker, "text": current_text.strip()})
            current_speaker, current_text = line.split(":", 1)
        else:
            current_text += f" {line}"

    if current_speaker and current_text.strip():
        dialog_parts.append({"speaker": current_speaker, "text": current_text.strip()})

    if not dialog_parts:
        dialog_parts = [{"speaker": "Anna", "text": dialog_text}]

    return dialog_parts


def create_final_audio(user_uuid: str, gripsbox_uuid: str, audio_file_paths: list):
    """
    Kombiniert alle Audiodateien und speichert sie im richtigen Ordner.
    """
    # Speicherpfad erstellen
    podcast_storage_path = "C:/projects/houdini/server/storage/audio/podcasts"
    user_gripsbox_path = os.path.join(podcast_storage_path, user_uuid, gripsbox_uuid)

    # Sicherstellen, dass der Ordner existiert
    os.makedirs(user_gripsbox_path, exist_ok=True)

    # Finale Datei erstellen
    final_audio_path = os.path.join(user_gripsbox_path, "final.mp3")

    # Die Audiodateien zusammenfügen
    combined = AudioSegment.empty()
    for file_path in audio_file_paths:
        audio = AudioSegment.from_mp3(file_path)
        combined += audio

    # Speichern der finalen Audiodatei
    combined.export(final_audio_path, format="mp3")

    logger.debug(f"Finale Datei gespeichert als: {final_audio_path}")
    return final_audio_path


from server.app.models.users.user import User


@router.post("/podcasts/elevenlabs", response_model=PodcastPostResponseModel, status_code=status.HTTP_201_CREATED,
             tags=["podcasts"])
async def create_podcast(gripsbox_data: PodcastGripsboxRequestModel, user: User = Depends(auth)):
    """
    Erstellt einen Podcast aus einer Gripsbox mit Textinhalt über ElevenLabs TTS.
    """
    gripsbox_id = gripsbox_data.gripsbox_id
    speakers = gripsbox_data.speakers
    logger.debug(f"Request erhalten - Gripsbox ID: {gripsbox_id}, Sprecher: {speakers}")

    try:
        text = await load_gripsbox_by_id(gripsbox_id)
        if isinstance(text, list):
            text = " ".join(text)
    except HTTPException as e:
        raise e

    if not text:
        logger.error("Gripsbox enthält keinen gültigen Text.")
        raise HTTPException(status_code=400, detail="Gripsbox enthält keinen Text.")

    dialog_text = generate_dialog_with_gpt4(text)

    dialog_parts = split_dialog_by_speakers(dialog_text, speakers)
    logger.debug(f"Parts: {dialog_parts}")

    dialogue = []
    for part in dialog_parts:
        speaker = part["speaker"]
        text_chunk = part["text"]
        voice_id = voice_map.get(speaker)
        if not voice_id:
            raise HTTPException(status_code=400, detail=f"Unbekannter Sprecher: {speaker}")
        dialogue.append({"voice_id": voice_id, "text": text_chunk})

    # Ersetze dies mit der tatsächlichen UUID des Benutzers
    audio_file_paths = create_elevenlabs_audio(dialogue, str(user.uuid), gripsbox_id)

    # Finales Audio erstellen
    final_audio_path = create_final_audio(str(user.uuid), gripsbox_id, audio_file_paths)

    return PodcastPostResponseModel(id=gripsbox_id, title="Gripsbox Podcast", audio_url=final_audio_path)
