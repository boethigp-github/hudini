from pydantic import BaseModel, Field

from uuid import UUID

from typing import List, Optional, Any, Dict
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
    completion: Optional[Dict[str, Any]] = None

class UserContextPostRequestModel(BaseModel):
    prompt_id: UUID
    user: str
    thread_id: int
    context_data: List[ContextDataItem]  # Allow a list of dictionaries
