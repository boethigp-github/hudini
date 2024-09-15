from pydantic import BaseModel, Field
from typing import List

class GripsboxPostRequestModel(BaseModel):
    name: str = Field(..., example="Grip A")
    size: int = Field(..., example=10, ge=1, description="Size of the gripsbox, must be a positive integer")
    type: str = Field(..., example="Type X")
    active: bool = Field(..., example=True)
    tags: List[str] = Field(..., example=["tag1", "tag2"])
    models: List[str] = Field(..., example=["gpt-3.5-turbo"])

    class Config:
        schema_extra = {
            "example": {
                "name": "Grip A",
                "size": 10,
                "type": "Type X",
                "active": True,
                "tags": ["tag1", "tag2"],
                "models": ["gpt-3.5-turbo"]
            }
        }
