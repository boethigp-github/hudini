from pydantic import BaseModel, EmailStr, ConfigDict
from datetime import datetime
from typing import Optional

class UsersGetResponseModel(BaseModel):
    id: int
    username: str
    email: EmailStr
    created_at: datetime
    last_login: Optional[datetime] = None

    # Updated for Pydantic v2
    model_config = ConfigDict(from_attributes=True)
