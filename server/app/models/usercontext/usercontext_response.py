from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, Dict, Any, List
from uuid import UUID
from datetime import datetime

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
    user: Optional[str] = None
    status: Optional[str] = None
    id: Optional[UUID] = None
    prompt_id: Optional[UUID] = None
    model: Optional[str] = None
    completion: Optional[Completion] = None

class UserContextResponseModel(BaseModel):
    id: int
    user: UUID
    thread_id: int
    created: datetime
    updated: datetime
    context_data: List[ContextDataItem]  # Allow a list of ContextDataItem objects

    class Config:
        orm_mode = True
        from_attributes = True  # Enable `model_validate` to work with SQLAlchemy models
