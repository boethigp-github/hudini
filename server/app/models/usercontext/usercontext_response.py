from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, Dict, Any
from uuid import UUID
from datetime import datetime

class UserContextResponseModel(BaseModel):
    id: int
    user_id: UUID
    thread_id: int
    created: datetime
    updated: datetime
    context_data: Optional[Dict[str, Any]]

    class Config:
        orm_mode = True
        from_attributes = True  # Enable `from_orm` method to work with SQLAlchemy models
