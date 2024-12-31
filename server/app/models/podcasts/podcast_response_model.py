from pydantic import BaseModel, Field, ConfigDict
from uuid import UUID

class PodcastPostResponseModel(BaseModel):
    id: UUID = Field(..., description="Eindeutige ID des Podcasts")
    title: str = Field(..., description="Titel des Podcasts")
    audio_url: str = Field(..., description="URL zur heruntergeladenen Audio-Datei")

    # Modellkonfiguration mit Beispieldaten
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "title": "KI und Ethik",
                "audio_url": "/static/550e8400-e29b-41d4-a716-446655440000.mp3"
            }
        }
    )
