# Original content of server/app/models/prompt.py
# (Keeping the original content, only changing int to UUID where necessary)

from pydantic import BaseModel, Field
from typing import Optional, Union

from uuid import UUID


class PromptPostRequestModel(BaseModel):
    prompt: str
    user: UUID  # Changed from int to UUID
    status: Optional[str] = None
    uuid: UUID

    class ConfigDict:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "prompt": "Test prompt",
                "user": "123e4567-e89b-12d3-a456-426614174000",
                "status": "IN_PROGRESS",
                "uuid": "123e4567-e89b-12d3-a456-426614174000"
            }
        }