from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

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
                "created_at": datetime.utcnow().isoformat(),  # Dynamic example using current time
            }
        }
