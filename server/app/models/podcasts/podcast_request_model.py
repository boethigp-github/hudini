from pydantic import BaseModel, Field, ConfigDict
from typing import List


class PodcastGripsboxRequestModel(BaseModel):
    gripsbox_id: str = Field(..., description="Gripsbox ID")
    speakers: List[str] = Field(default=["Anna", "Tom"], description="Liste der Sprecher")

    # Beispiel für die Verwendung von json_schema_extra
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "gripsbox_id": "123e4567-e89b-12d3-a456-426614174000",
                "speakers": ["Anna", "Tom"]
            }
        }
    )
