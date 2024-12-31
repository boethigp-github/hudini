import os
import logging
from gtts import gTTS
from pydub import AudioSegment
from uuid import uuid4
from server.app.models.prompts.prompt_post_response_model import PromptPostResponseModel
from server.app.config.settings import Settings

# Logging initialisieren
settings = Settings()
logger = logging.getLogger(__name__)


class PodcastService:
    # Verzeichnisse konfigurieren
    STATIC_PATH = settings.get("default").get("APP_STORAGE") + "/storage/audio/podcast"
    INPUT_PATH = STATIC_PATH + "/input"
    OUTPUT_PATH = STATIC_PATH + "/output"
    LANGUAGE = "de"


    def generate_podcast(title: str, content: str, speakers: list) -> PromptPostResponseModel:
        """
        Erzeugt einen dialogischen Podcast aus dem Inhalt und den Sprechern.
        """
        logger.info(f"Podcast wird generiert: {title}")
        audio_segments = []

        # Sicherstellen, dass Verzeichnisse existieren
        os.makedirs(PodcastService.INPUT_PATH, exist_ok=True)
        os.makedirs(PodcastService.OUTPUT_PATH, exist_ok=True)

        # --- INTRO HINZUFÜGEN ---
        intro_path = os.path.join(PodcastService.INPUT_PATH, "intro.mp3")
        if os.path.exists(intro_path):
            intro = AudioSegment.from_mp3(intro_path)
            audio_segments.append(intro)
        else:
            logger.warning("Intro-Datei fehlt. Überspringe Intro.")

        # --- DIALOG GENERIEREN ---
        sentences = content.split(". ")
        temp_files = []  # Für Cleanup

        try:
            for i, sentence in enumerate(sentences):
                speaker = speakers[i % len(speakers)]  # Sprecher abwechseln
                logger.debug(f"{speaker} sagt: {sentence}")

                # Text-to-Speech für jeden Satz
                temp_filename = os.path.join(PodcastService.INPUT_PATH, f"temp_{uuid4()}.mp3")
                tts = gTTS(text=f"{speaker} sagt: {sentence}", lang=PodcastService.LANGUAGE)
                tts.save(temp_filename)

                # Datei in Audio umwandeln
                audio = AudioSegment.from_mp3(temp_filename)
                audio_segments.append(audio)
                temp_files.append(temp_filename)  # Datei zum Löschen vormerken

            # --- OUTRO HINZUFÜGEN ---
            outro_path = os.path.join(PodcastService.INPUT_PATH, "outro.mp3")
            if os.path.exists(outro_path):
                outro = AudioSegment.from_mp3(outro_path)
                audio_segments.append(outro)
            else:
                logger.warning("Outro-Datei fehlt. Überspringe Outro.")

            # --- AUDIO ZUSAMMENFÜGEN ---
            podcast = sum(audio_segments)
            output_file = os.path.join(PodcastService.OUTPUT_PATH, f"{uuid4()}.mp3")
            podcast.export(output_file, format="mp3")

            logger.info(f"Podcast gespeichert: {output_file}")

            # --- RESPONSE MODELL ---
            return PromptPostResponseModel(
                id=uuid4(),
                title=title,
                audio_url=f"/storage/audio/podcast/output/{os.path.basename(output_file)}"
            )

        except Exception as e:
            logger.error(f"Fehler beim Erstellen des Podcasts: {str(e)}")
            raise RuntimeError(f"Fehler beim Erstellen des Podcasts: {str(e)}")

        finally:
            # --- CLEANUP ---
            for file in temp_files:
                if os.path.exists(file):
                    os.remove(file)
                    logger.debug(f"Temp-Datei gelöscht: {file}")
