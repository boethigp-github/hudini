from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from uuid import UUID
from datetime import datetime

class UserContextModel(BaseModel):
    id: int  # Auto-incrementing primary key
    user_id: UUID = Field(default_factory=UUID)  # UUID, automatically generated
    created: datetime = Field(default_factory=datetime.utcnow)  # Creation timestamp, default to current time
    updated: datetime = Field(default_factory=datetime.utcnow)  # Update timestamp, default to current time
    context_data: Optional[Dict[str, Any]] = None  # JSONB field for context data

    class Config:
        orm_mode = True