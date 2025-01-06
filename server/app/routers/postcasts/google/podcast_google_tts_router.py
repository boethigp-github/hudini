import os
import logging
from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from server.app.config.settings import Settings
from server.app.utils.auth import auth
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


import os
import logging
from uuid import uuid4
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field
import re
import json
from google.cloud import texttospeech
from server.app.config.settings import Settings
from server.app.services.gripsbox_service import load_gripsbox_by_id
from server.app.models.podcasts.podcast_response_model import PodcastPostResponseModel
from openai import OpenAI

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




import random
import re
from google.cloud import texttospeech
from fastapi import HTTPException

def remove_speaker_names(dialog: str):
    """
    Entfernt die Sprecher-Namen (Anna:, Tom:) aus dem Dialog.
    """
    cleaned_dialog = re.sub(r"^(Anna:|Tom:)\s*", "", dialog)
    return cleaned_dialog

def generate_dialog_with_random_addressing(dialog: str, speakers: list):
    """
    Generiert einen Dialog und lässt ab und zu den Sprecher den anderen ansprechen.
    Verhindert, dass der Sprecher sich mit seinem eigenen Namen anspricht.
    """
    sentences = dialog.split('\n')
    new_dialog = []

    for sentence in sentences:
        # Wahrscheinlichkeit für das Ansprechen des anderen Sprechers
        if random.random() < 0.2:  # 20% Chance
            current_speaker = random.choice(speakers)  # Wählt zufällig einen Sprecher
            other_speaker = [s for s in speakers if s != current_speaker][0]  # Der andere Sprecher
            addressed_sentence = f"{other_speaker}, {sentence}"  # Ansprache des anderen Sprechers
            new_dialog.append(addressed_sentence)
        else:
            new_dialog.append(sentence)

    return '\n'.join(new_dialog)


def synthesize_google_speech(text_chunks: list, voice_name: str, language_code: str = "de-DE"):
    """
    Erstellt Sprache aus Textblöcken mit der Google TTS-API unter Verwendung von SSML.
    Entfernt die Sprecher-Namen, stellt sicher, dass sie nicht vorgelesen werden,
    fügt Atempausen und zufällige Ansprachen hinzu.
    """
    client = texttospeech.TextToSpeechClient(client_options={"api_key": GOOGLE_API_KEY})
    audio_content = b""

    for i, chunk in enumerate(text_chunks):
        logger.debug(f"Verarbeite Chunk {i+1}/{len(text_chunks)}: {chunk[:50]}...")

        # Entferne die Sprecher-Namen und lasse den Dialog natürlicher klingen
        cleaned_dialog = remove_speaker_names(chunk)

        # Generiere den Dialog mit zufälliger Ansprache des anderen Sprechers
        updated_dialog = generate_dialog_with_random_addressing(cleaned_dialog, ["Anna", "Tom"])

        # SSML-Text vorbereiten, der den Dialog enthält, mit Atempausen
        ssml_text = f"""
        <speak>
            <voice name="{voice_name}">
                <prosody rate="medium" pitch="medium" volume="medium">
                    {updated_dialog}  <!-- Der Satz wird ohne Sprechername in SSML eingebunden -->
                </prosody>
            </voice>
            <break time="{random.choice([150, 200, 300])}ms"/>
        </speak>
        """

        # Eingabetext konfigurieren
        input_text = texttospeech.SynthesisInput(ssml=ssml_text)

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



def generate_dialog_with_gpt4(text: str):
    """
    Nutzt GPT-4, um den Text in Dialogform zu konvertieren.
    """
    try:
        API_KEY_OPEN_AI = settings.get("default").get("API_KEY_OPEN_AI")
        # OpenAI Client mit API-Schlüssel initialisieren
        client = OpenAI(api_key=API_KEY_OPEN_AI)

        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Du bist ein Dialog-Generator. "
                        "Teile den gegebenen Text in einen natürlichen Dialog zwischen zwei Sprechern auf. "
                        "Nutze abwechselnd die Namen 'Anna' und 'Tom' und erzeuge realistische Konversationen."
                    )
                },
                {"role": "user", "content": text}  # Übergabe des Textinhalts
            ],
            temperature=0.7,
            max_tokens=2000,
        )
        # Ergebnis extrahieren
        dialog = response.choices[0].message.content
        return dialog
    except Exception as e:
        logger.error(f"OpenAI API-Fehler: {str(e)} for api_key: {API_KEY_OPEN_AI}")
        raise HTTPException(status_code=500, detail=f"OpenAI API-Fehler: {str(e)} for api_key: {API_KEY_OPEN_AI}")




@router.post("/podcasts", response_model=PodcastPostResponseModel, status_code=status.HTTP_201_CREATED,  tags=["podcasts"])
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

    # 2. Text in Dialogform bringen
    dialog_text = generate_dialog_with_gpt4(text)

    # Entferne die Sprecher-Namen
    cleaned_dialog = remove_speaker_names(dialog_text)

    # Teile den Dialog in Sätze auf
    sentences = re.split(r'(?<=[.!?])\s+', cleaned_dialog)

    # 3. Stimmen für den Dialog festlegen
    voice_map = {"Anna": "de-DE-Wavenet-C", "Tom": "de-DE-Wavenet-B"}
    audio_content = b""

    # 4. Audio generieren
    for i, sentence in enumerate(sentences):
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

    # 6. Dialog als JSON speichern
    dialog_data = {
        "gripsbox_id": gripsbox_id,
        "speakers": speakers,
        "dialog": cleaned_dialog,
    }
    with open(f"{podcast_id}_dialog.json", "w") as json_file:
        json.dump(dialog_data, json_file, ensure_ascii=False, indent=4)

    return PodcastPostResponseModel(id=podcast_id, title="Gripsbox Podcast", audio_url=file_path)











def remove_speaker_names(dialog: str):
    """
    Entfernt die Sprecher-Namen (Anna:, Tom:) aus dem Dialog.
    """
    # Regulärer Ausdruck, um die Sprecher-Namen zu entfernen
    cleaned_dialog = re.sub(r"^(Anna:|Tom:)\s*", "", dialog)
    return cleaned_dialog


@router.post("/podcasts", response_model=PodcastPostResponseModel, status_code=status.HTTP_201_CREATED,  tags=["podcasts"])
async def create_podcast(gripsbox_data: PodcastGripsboxRequestModel,  _: str = Depends(auth)):
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

    # 2. Text in Dialogform bringen
    dialog_text = generate_dialog_with_gpt4(text)

    # Entferne die Sprecher-Namen
    cleaned_dialog = remove_speaker_names(dialog_text)

    # Teile den Dialog in Sätze auf
    sentences = re.split(r'(?<=[.!?])\s+', cleaned_dialog)

    # 3. Stimmen für den Dialog festlegen
    voice_map = {"Anna": "de-DE-Wavenet-C", "Tom": "de-DE-Wavenet-B"}
    audio_content = b""

    # 4. Audio generieren
    for i, sentence in enumerate(sentences):
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

    # 6. Dialog als JSON speichern
    dialog_data = {
        "gripsbox_id": gripsbox_id,
        "speakers": speakers,
        "dialog": cleaned_dialog,
    }
    with open(f"{podcast_id}_dialog.json", "w") as json_file:
        json.dump(dialog_data, json_file, ensure_ascii=False, indent=4)

    return PodcastPostResponseModel(id=podcast_id, title="Gripsbox Podcast", audio_url=file_path)

