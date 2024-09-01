from pydantic import BaseModel, Field, ConfigDict
from typing import Literal
from datetime import datetime, timezone
import random


def utc_now():
    return datetime.now(timezone.utc)

def generate_bigint():
    return random.randint(1, 1000000)


# Pydantic model
class StreamResponse(BaseModel):
    status: Literal['data', 'end', 'error'] = Field(..., description="Status of the stream (e.g., start, data, end, error)")
    model: str = Field('', description="The name of the model being used")
    message: str = Field('', description="Additional information or error messages")
    token: str = Field('', description="The generated token or word from the model")
    user: int = Field(default_factory=generate_bigint, description="The user associated with the request")  # Changed to bigint
    timestamp: datetime = Field(default_factory=utc_now, description="The time at which the event occurred")
    prompt: str = Field('', description="The prompt that was used for generation")
    id: int = Field(default_factory=generate_bigint, description="The prompt ID that was used for generation")  # Changed to bigint

    def to_dict(self):
        return {
            "status": self.status,
            "model": self.model,
            "message": self.message,
            "token": self.token,
            "user": self.user,
            "timestamp": self.timestamp.isoformat(),
            "prompt": self.prompt,
            "id": self.id
        }

    # Updated Config using ConfigDict
    model_config = ConfigDict(
        from_attributes=True
    )
