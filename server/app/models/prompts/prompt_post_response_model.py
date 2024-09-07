from pydantic import BaseModel, Field
from typing import Optional, Union
from datetime import datetime
from uuid import UUID


class PromptPostResponseModel(BaseModel):
    prompt: str
    user: UUID
    status: Optional[str] = None
    created: datetime = datetime.utcnow()
    uuid: UUID


    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "prompt": "Test prompt",
                "user": "123e4567-e89b-12d3-a456-426614174000",
                "status": "IN_PROGRESS",
                "created": str(datetime.utcnow()),
                "uuid": "123e4567-e89b-12d3-a456-426614174000"
            }
        }
