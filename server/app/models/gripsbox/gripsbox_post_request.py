from pydantic import BaseModel, Field
from typing import List

class GripsboxPostRequestModel(BaseModel):
    name: str = Field(..., description="Name of the gripsbox")
    size: int = Field(..., ge=1, description="Size of the gripsbox, must be a positive integer")
    type: str = Field(..., description="Type of the gripsbox")
    active: bool = Field(..., description="Whether the gripsbox is active")
    tags: List[str] = Field(..., description="List of tags associated with the gripsbox")
    models: List[str] = Field(..., description="List of models associated with the gripsbox")

    class ConfigDict:
        # Correct usage of json_schema_extra for Pydantic V2
        json_schema_extra = {
            "example": {
                "name": "Grip A",
                "size": 10,
                "type": "Type X",
                "active": True,
                "tags": ["tag1", "tag2"],
                "models": ["gpt-3.5-turbo"]
            }
        }
