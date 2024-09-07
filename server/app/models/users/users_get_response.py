from pydantic import BaseModel, EmailStr, ConfigDict
from datetime import datetime
from typing import Optional
from uuid import UUID
class UsersGetResponseModel(BaseModel):
    uuid: UUID  # Changed from 'id: int' to 'uuid: UUID'
    username: str
    email: EmailStr
    created: datetime
    last_login: Optional[datetime] = None

    # Updated for Pydantic v2
    model_config = ConfigDict(from_attributes=True)
