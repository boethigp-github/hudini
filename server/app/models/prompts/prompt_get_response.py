from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime, timezone

class PromptGetResponseModel(BaseModel):
    id: int
    prompt: str
    user: int
    status: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "prompt": "Test prompt",
                "user": 123,
                "status": "initialized",
                "created_at": datetime.now(timezone.utc).isoformat(),  # Current timestamp in ISO format
            }
        }
