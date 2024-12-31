from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from uuid import UUID
import pytz
from server.app.config.settings import Settings
settings = Settings()


class PromptPostResponseModel(BaseModel):
    prompt: str
    user: UUID
    status: Optional[str] = None
    created: datetime = Field(default_factory=lambda: datetime.now(
        tz=pytz.timezone(settings.get("default").get("APP_TIMEZONE"))))  # Add timezone-aware datetime

    uuid: UUID

    class ConfigDict:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "prompt": "Test prompt",
                "user": "123e4567-e89b-12d3-a456-426614174000",
                "status": "IN_PROGRESS",
                "created": str(datetime.now(
                    tz=pytz.timezone(settings.get("default").get("APP_TIMEZONE")))),
                "uuid": "123e4567-e89b-12d3-a456-426614174000"
            }
        }
