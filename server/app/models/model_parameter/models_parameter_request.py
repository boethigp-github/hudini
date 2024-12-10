from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from uuid import UUID


class ModelParameterRequestModel(BaseModel):
    user: UUID = Field(..., description="The unique identifier of the user.")
    parameter: Optional[str] = Field(None, max_length=200, description="Name of the parameter (max 200 characters).")
    model: Optional[str] = Field(None, max_length=200, description="Name of the model (max 200 characters).")
    value: Optional[dict] = Field(None, description="JSON object representing the value of the parameter.")
    active: bool = Field(False, description="Whether the model parameter is active.")

    # Example usage
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "user": "123e4567-e89b-12d3-a456-426614174000",
                "parameter": "max_tokens",
                "model": "gpt-4",
                "value": {"max": 1024},
                "active": True
            }
        }
    )
