from pydantic import BaseModel, Field
from typing import Optional
from uuid import UUID
from datetime import datetime


class ModelParameterResponseModel(BaseModel):
    uuid: UUID = Field(..., description="The unique identifier for the model parameter.")
    user: UUID = Field(..., description="The unique identifier of the user.")
    parameter: Optional[str] = Field(None, description="Name of the parameter.")
    model: Optional[str] = Field(None, description="Name of the model.")
    value: Optional[dict] = Field(None, description="JSON object representing the parameter's value.")
    active: bool = Field(..., description="Indicates whether the parameter is active.")
    created: datetime = Field(..., description="Timestamp when the parameter was created.")
    updated: Optional[datetime] = Field(None, description="Timestamp when the parameter was last updated.")

    class ConfigDict:
        json_schema_extra = {
            "example": {
                "uuid": "123e4567-e89b-12d3-a456-426614174000",
                "user": "123e4567-e89b-12d3-a456-426614174000",
                "parameter": "max_tokens",
                "model": "gpt-4",
                "value": {"max": 1024},
                "active": True,
                "created": "2024-01-01T00:00:00Z",
                "updated": "2024-01-02T12:00:00Z"
            }
        }
