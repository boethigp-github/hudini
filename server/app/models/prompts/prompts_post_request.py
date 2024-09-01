from pydantic import BaseModel, Field, field_validator, ValidationError
from typing import Optional
from uuid import UUID, uuid4
from enum import Enum as PyEnum


class StatusEnum(PyEnum):
    INITIALIZED = "INITIALIZED"
    PROMPT_SAVED = "PROMPT_SAVED"
    PROMPT_UPDATED = "PROMPT_UPDATED"
    PROMPT_DELETED = "PROMPT_DELETED"
    COMPLETED = "COMPLETED"
    IN_PROGRESS = "IN_PROGRESS"
    FAILED = "FAILED"


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

    @field_validator("status")
    def validate_status(cls, value):
        if value not in StatusEnum.__members__:
            raise ValueError(f"Invalid status: {value}. Must be one of {list(StatusEnum.__members__.keys())}")
        return value

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "prompt": "Test prompt",
                "user": 123,
                "status": "INITIALIZED",
                "uuid": "123e4567-e89b-12d3-a456-426614174000",  # Example UUID
            }
        }
