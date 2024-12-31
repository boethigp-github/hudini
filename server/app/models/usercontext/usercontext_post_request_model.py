from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from uuid import UUID, uuid4
from datetime import datetime
import pytz
from server.app.config.settings import Settings
settings = Settings()

class Message(BaseModel):
    content: str
    refusal: Optional[str] = None
    role: str

    class ConfigDict:
        json_encoders = {
            UUID: lambda v: str(v)  # Automatically serialize UUIDs to strings
        }


class Choice(BaseModel):
    finish_reason: Optional[str] = None
    index: int
    logprobs: Optional[Any] = None
    message: Message

    class ConfigDict:
        json_encoders = {
            UUID: lambda v: str(v)  # Automatically serialize UUIDs to strings
        }


class Usage(BaseModel):
    completion_tokens: int
    prompt_tokens: int
    total_tokens: int

    class ConfigDict:
        json_encoders = {
            UUID: lambda v: str(v)  # Automatically serialize UUIDs to strings
        }


class Completion(BaseModel):
    id: str
    choices: List[Choice]
    created: int
    model: str
    object: str
    system_fingerprint: Optional[str] = None
    usage: Usage

    class ConfigDict:
        json_encoders = {
            UUID: lambda v: str(v)  # Automatically serialize UUIDs to strings
        }


class ContextDataItem(BaseModel):
    id: UUID = Field(default_factory=uuid4) 
    user: Optional[UUID] = None
    status: Optional[str] = None
    model: Optional[str] = None
    completion: Optional[Dict[str, Any]] = None

    class ConfigDict:
        json_encoders = {
            UUID: lambda v: str(v)  # Automatically serialize UUIDs to strings
        }


class UserContextPromptModel(BaseModel):
    prompt: str = ""  # Set default to empty string
    uuid: UUID
    user: UUID
    status: Optional[str] = None
    created: datetime = Field(default_factory=lambda: datetime.now(tz=pytz.timezone(settings.get("default").get("APP_TIMEZONE"))))  # Add timezone-aware datetime
    context_data: List[ContextDataItem]  # Add context_data here

    class ConfigDict:
        from_attributes = True
        json_encoders = {
            UUID: lambda v: str(v)  # Automatically serialize UUIDs to strings
        }
        json_schema_extra = {
            "example": {
                "prompt": "Test prompt",
                "user": "123e4567-e89b-12d3-a456-426614174000",
                "status": "IN_PROGRESS",
                "created": "2024-09-06T12:00:00+01:00",  # Example with timezone
                "uuid": "123e4567-e89b-12d3-a456-426614174000",
                "context_data": []  # Example field
            }
        }


class UserContextPrompt(BaseModel):
    user: UUID
    uuid: UUID
    status: str
    prompt: str
    context_data: List[ContextDataItem]  # Hier fügen wir den korrekten Typ für context_data hinzu!

    class ConfigDict:
        json_encoders = {
            UUID: lambda v: str(v)  # Automatically serialize UUIDs to strings
        }


class UserContextPostRequestModel(BaseModel):
    uuid: UUID
    user: UUID
    thread_id: int
    prompt: UserContextPrompt

    class ConfigDict:
        from_attributes = True
        json_encoders = {
            UUID: lambda v: str(v)  # Automatically serialize UUIDs to strings
        }
