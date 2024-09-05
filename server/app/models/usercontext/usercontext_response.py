from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, Any, List
from datetime import datetime
from uuid import UUID,uuid4

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
    started: int = Field(default_factory=lambda: int(datetime.utcnow().timestamp()), example=1633046400)
    ended: int = Field(default_factory=lambda: int(datetime.utcnow().timestamp()), example=1633046400)
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
    id: UUID = Field(default_factory=uuid4)
    model: Optional[str] = None
    completion: Optional[dict] = None

class UserContextResponseModel(BaseModel):
    id: int
    user: int
    thread_id: int
    created: datetime
    updated: datetime
    context_data: List[ContextDataItem]

    model_config = ConfigDict(
        from_attributes=True,
        protected_namespaces=()
    )

class UserContextPostRequestModel(BaseModel):
    user: int
    thread_id: int
    context_data: List[ContextDataItem]