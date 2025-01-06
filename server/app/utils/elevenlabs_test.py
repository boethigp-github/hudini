import requests
import json

url = "https://api.elevenlabs.io/v1/text-to-speech"  # Einzelner TTS-Endpunkt!
api_key = "sk_bed7830b6ffdee30b8e15c11d68908b5d091e868cf02b736"

headers = {
    "Content-Type": "application/json",
    "xi-api-key": api_key
}

# Einzelne Anfragen für jede Stimme
dialogue = [
    {"voice_id": "IKne3meq5aSn9XLyUdCD", "text": "Hallo Tom, hast du das neueste KI-Modell gesehen?"},
    {"voice_id": "N2lVS1w4EtoT3dr4eOWO", "text": "Ja, Anna! Es scheint, als würde es den Markt revolutionieren."},
    {"voice_id": "nPczCjzI2devNBz1zQrb", "text": "Das könnte ein echter Game-Changer sein."}
]

audio_files = []
for line in dialogue:
    payload = {
        "model_id": "eleven_multilingual_v1",
        "text": line["text"],  # Einzelner Text!
        "voice_settings": {
            "stability": 0.75,
            "similarity_boost": 0.85
        }
    }
    response = requests.post(f"{url}/{line['voice_id']}", headers=headers, data=json.dumps(payload))

    if response.status_code == 200:
        file_name = f"C:/projects/houdini/server/storage/audio/podcasts/output_{line['voice_id']}.mp3"
        with open(file_name, "wb") as audio_file:
            audio_file.write(response.content)
        audio_files.append(file_name)
        print(f"Audio erfolgreich erstellt: {file_name}")
    else:
        print(f"Fehler: {response.status_code}")
        print(response.text)

print("Alle Dateien:", audio_files)
