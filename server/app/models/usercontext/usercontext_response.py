from pydantic import BaseModel , field_validator
from typing import Optional, Dict, Any, List
from datetime import datetime
from uuid import UUID, uuid4
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
    user: Optional[int] = None  # Changed from str to int for bigint
    status: Optional[str] = None
    id: Optional[int] = None

    model: Optional[str] = None
    completion: Optional[Completion] = None

class UserContextResponseModel(BaseModel):
    id: int  
    user: int  
    thread_id: int
    prompt_uuid: UUID  # Add the UUID field
    created: datetime
    updated: datetime
    context_data: List[ContextDataItem]  # Allow a list of ContextDataItem objects

    @field_validator("prompt_uuid")
    def validate_prompt_uuid(cls, value):
        if not isinstance(value, UUID):
            raise ValueError("Invalid UUID format")
        return value

    class Config:
        orm_mode = True
        from_attributes = True
        protected_namespaces=() #conflict with model_
