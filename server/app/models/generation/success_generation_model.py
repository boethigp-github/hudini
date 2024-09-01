from pydantic import BaseModel, Field
from typing import List, Optional

class Message(BaseModel):
    content: str = Field(..., example="This is a sample message content.")
    refusal: Optional[str] = Field(None, example="Sample refusal message.")
    role: str = Field(..., example="assistant")

class Choice(BaseModel):
    finish_reason: str = Field(..., example="stop")
    index: int = Field(..., example=0)
    logprobs: Optional[dict] = Field(None, example={"logprobs": "sample logprobs"})
    message: Message

class Usage(BaseModel):
    completion_tokens: int = Field(..., example=50)
    prompt_tokens: int = Field(..., example=100)
    total_tokens: int = Field(..., example=150)

class Completion(BaseModel):
    id: str = Field(..., example="abc123")
    choices: List[Choice]
    created: int = Field(..., example=1633046400)  # Example timestamp
    model: str = Field(..., example="gpt-3.5-turbo")
    object: str = Field(..., example="text_completion")
    system_fingerprint: Optional[str] = Field(None, example="fingerprint123")
    usage: Usage

class SuccessGenerationModel(BaseModel):
    id: str = Field(..., example="gen-xyz-456")
    model: str = Field(..., example="gpt-3.5-turbo")
    completion: Completion
