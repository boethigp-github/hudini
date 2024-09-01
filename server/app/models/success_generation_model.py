from pydantic import BaseModel, Field
from typing import List, Optional

class Message(BaseModel):
    content: str
    refusal: Optional[str] = None
    role: str

class Choice(BaseModel):
    finish_reason: str
    index: int
    logprobs: Optional[dict] = None
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
    system_fingerprint: Optional[str] = None  # Allow None
    usage: Usage

class SuccessGenerationModel(BaseModel):
    id:str
    model: str
    completion: Completion
