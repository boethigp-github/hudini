from pydantic import BaseModel, EmailStr, ConfigDict, Field
from datetime import datetime
from typing import Optional
from uuid import UUID
import pytz
from server.app.config.settings import Settings
settings = Settings()

class UsersGetResponseModel(BaseModel):
    uuid: UUID  # Changed from 'id: int' to 'uuid: UUID'
    username: str
    email: EmailStr
    created: datetime = Field(default_factory=lambda: datetime.now(
        tz=pytz.timezone(settings.get("default").get("APP_TIMEZONE"))))
    last_login: Optional[datetime] = None

    # Updated for Pydantic v2
    model_config = ConfigDict(from_attributes=True)
