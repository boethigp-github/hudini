# server/app/models/usercontext/usercontext_post_request_model.py

from pydantic import BaseModel, Field
from typing import Optional, List
from uuid import UUID
from datetime import datetime
import pytz
from server.app.config.settings import Settings
settings = Settings()
class ContextDataItem(BaseModel):
    prompt_uuid: UUID
    user: Optional[UUID] = None
    status: Optional[str] = None
    model: Optional[str] = None
    completion: Optional[dict] = None

    class Config:
        json_encoders = {
            UUID: lambda v: str(v)  # Automatically serialize UUIDs to strings
        }

class UserContextPromptModel(BaseModel):
    prompt: str = ""  # Set default to empty string
    uuid: UUID
    user: UUID
    status: Optional[str] = None
    created: datetime = Field(default_factory=lambda: datetime.now(
        tz=pytz.timezone(settings.get("default").get("APP_TIMEZONE"))))  # Add timezone-aware datetime

    class Config:
        from_attributes = True
        json_encoders = {
            UUID: lambda v: str(v)  # Automatically serialize UUIDs to strings
        }
        json_schema_extra = {
            "example": {
                "prompt": "Test prompt",
                "user": "123e4567-e89b-12d3-a456-426614174000",
                "status": "IN_PROGRESS",
                "created": "2024-09-06T12:00:00",
                "uuid": "123e4567-e89b-12d3-a456-426614174000"
            }
        }

class UserContextPostRequestModel(BaseModel):
    uuid: UUID
    user: UUID
    thread_id: int
    prompt: UserContextPromptModel
    context_data: List[ContextDataItem]

    class Config:
        json_encoders = {
            UUID: lambda v: str(v)  # Automatically serialize UUIDs to strings
        }
# server/app/models/usercontext/usercontext_post_response_model.py

from pydantic import BaseModel
from uuid import UUID
from server.app.models.usercontext.usercontext_post_request_model import UserContextPromptModel

class UserContextResponseModel(BaseModel):
    uuid: UUID
    user: UUID
    thread_id: int
    prompt: UserContextPromptModel  # This model now includes context_data

    class Config:
        from_attributes = True
        json_encoders = {
            UUID: lambda v: str(v)
        }