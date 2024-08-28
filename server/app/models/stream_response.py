
from pydantic import BaseModel, Field, ConfigDict
from typing import Literal
from uuid import UUID as UUIDType
from datetime import datetime, timezone
from uuid import uuid4


def utc_now():
    return datetime.now(timezone.utc)

def uuid():
    return uuid4()



# Pydantic model
class StreamResponse(BaseModel):
    status: Literal['data', 'end', 'error'] = Field(..., description="Status of the stream (e.g., start, data, end, error)")
    model: str = Field('', description="The name of the model being used")
    message: str = Field('', description="Additional information or error messages")
    token: str = Field('', description="The generated token or word from the model")
    user: str = Field('anonymous', description="The user associated with the request")
    timestamp: datetime = Field(default_factory=utc_now, description="The time at which the event occurred")
    prompt: str = Field('', description="The prompt that was used for generation")
    prompt_id: UUIDType = Field(default_factory=uuid, description="The prompt ID that was used for generation")



    def to_dict(self):
        return {
            "status": self.status,
            "model": self.model,
            "message": self.message,
            "token": self.token,
            "user": self.user,
            "timestamp": self.timestamp.isoformat(),
            "prompt": self.prompt,
            "prompt_id": str(self.prompt_id)
        }

    # Updated Config using ConfigDict
    model_config = ConfigDict(
        from_attributes=True
    )
