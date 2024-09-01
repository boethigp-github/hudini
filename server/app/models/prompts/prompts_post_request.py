from pydantic import BaseModel, Field, field_validator
from typing import Optional
from uuid import UUID, uuid4

class PromptPostRequestModel(BaseModel):
    prompt: str = Field(..., description="The text of the prompt")
    user: int = Field(..., description="The ID of the user associated with the prompt")
    status: Optional[str] = Field(None, description="The status of the prompt, if applicable")
    uuid: UUID = Field(..., description="A unique identifier for the prompt")

    @field_validator("uuid")
    def validate_uuid(cls, value):
        if value:
            return str(value)  # Convert UUID to string
        return value

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "prompt": "Test prompt",
                "user": 123,
                "status": "initialized",
                "uuid": "123e4567-e89b-12d3-a456-426614174000",  # Example UUID
            }
        }
