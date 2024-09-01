from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime, timezone
from uuid import UUID

class PromptGetResponseModel(BaseModel):
    id: int
    prompt: str
    user: int
    status: Optional[str] = None
    created_at: datetime
    uuid: UUID  # Add the UUID field

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "prompt": "Test prompt",
                "user": 123,
                "status": "initialized",
                "created_at": datetime.now(timezone.utc).isoformat(),
                "uuid": "123e4567-e89b-12d3-a456-426614174000",  # Example UUID
            }
        }
