from pydantic import BaseModel, Field, ConfigDict
from typing import Optional


class ModelParameterRequestModel(BaseModel):
    parameter: Optional[str] = Field(None, max_length=200, description="Name of the parameter (max 200 characters).")
    model: Optional[str] = Field(None, max_length=200, description="Name of the model (max 200 characters).")
    value: Optional[dict] = Field(None, description="JSON object representing the value of the parameter.")
    active: bool = Field(False, description="Whether the model parameter is active.")

    # Example usage
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "parameter": "max_tokens",
                "model": "gpt-4",
                "value": {"max": 1024},
                "active": True
            }
        }
    )
