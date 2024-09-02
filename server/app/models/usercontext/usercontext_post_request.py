from pydantic import BaseModel, Field, field_validator
from typing import List, Optional, Dict, Any
from uuid import UUID

class Message(BaseModel):
    content: str
    refusal: Optional[str] = None
    role: str

class Choice(BaseModel):
    finish_reason: Optional[str] = None
    index: int
    logprobs: Optional[Any] = None
    message: Message

class Usage(BaseModel):
    completion_tokens: int
    prompt_tokens: int
    total_tokens: int

class Completion(BaseModel):
    id: str
    choices: List[Choice]
    created: int
    model: str
    object: str
    system_fingerprint: Optional[str] = None
    usage: Usage

class ContextDataItem(BaseModel):
    prompt: Optional[str] = None
    user: Optional[int] = None
    status: Optional[str] = None
    model: Optional[str] = None
    completion: Optional[Dict[str, Any]] = None

class UserContextPostRequestModel(BaseModel):
    prompt_uuid: UUID = Field(..., description="A unique identifier for the prompt")
    user: int
    thread_id: int
    context_data: List[ContextDataItem]

    @field_validator("prompt_uuid")
    def validate_prompt_uuid(cls, value):
        if not isinstance(value, UUID):
            raise ValueError("Invalid UUID format")
        return value
