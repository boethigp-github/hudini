from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional

class Message(BaseModel):
    content: str = Field(..., description="The content of the message.")
    refusal: Optional[str] = Field(None, description="Optional refusal message.")
    role: str = Field(..., description="Role of the message sender.")

    # Use ConfigDict instead of class Config
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "content": "This is a sample message content.",
                "refusal": "Sample refusal message.",
                "role": "assistant"
            }
        }
    )

class Choice(BaseModel):
    finish_reason: str = Field(..., description="The reason for completion of the message.")
    index: int = Field(..., description="The index of the choice.")
    logprobs: Optional[dict] = Field(None, description="Log probabilities of the completion.")
    message: Message

    # Use ConfigDict instead of class Config
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "finish_reason": "stop",
                "index": 0,
                "logprobs": {"logprobs": "sample logprobs"},
                "message": {
                    "content": "This is a sample message content.",
                    "refusal": "Sample refusal message.",
                    "role": "assistant"
                }
            }
        }
    )

class Usage(BaseModel):
    completion_tokens: int = Field(..., description="Number of completion tokens used.")
    prompt_tokens: int = Field(..., description="Number of prompt tokens used.")
    total_tokens: int = Field(..., description="Total number of tokens used.")
    started: int = Field(int(datetime.utcnow().timestamp()), description="Timestamp of when the completion started.")
    ended: int = Field(int(datetime.utcnow().timestamp()), description="Timestamp of when the completion ended.")

    # Use ConfigDict instead of class Config
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "completion_tokens": 50,
                "prompt_tokens": 100,
                "total_tokens": 150,
                "started": 1633046400,
                "ended": 1633046400
            }
        }
    )

class Completion(BaseModel):
    id: str = Field(..., description="Unique identifier for the completion.")
    choices: List[Choice]
    created: int = Field(..., description="Timestamp of when the completion was created.")
    model: str = Field(..., description="The model used for the completion.")
    object: str = Field(..., description="The type of object returned.")
    system_fingerprint: Optional[str] = Field(None, description="Optional fingerprint of the system.")
    usage: Usage

    # Use ConfigDict instead of class Config
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "id": "abc123",
                "choices": [{
                    "finish_reason": "stop",
                    "index": 0,
                    "logprobs": {"logprobs": "sample logprobs"},
                    "message": {
                        "content": "This is a sample message content.",
                        "refusal": "Sample refusal message.",
                        "role": "assistant"
                    }
                }],
                "created": 1633046400,
                "model": "gpt-3.5-turbo",
                "object": "text_completion",
                "system_fingerprint": "fingerprint123",
                "usage": {
                    "completion_tokens": 50,
                    "prompt_tokens": 100,
                    "total_tokens": 150,
                    "started": 1633046400,
                    "ended": 1633046400
                }
            }
        }
    )

class SuccessGenerationModel(BaseModel):
    id: str = Field(..., description="ID of the generated model.")
    model: str = Field(..., description="Model used for the generation.")
    completion: Completion

    # Use ConfigDict instead of class Config
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "id": "gen-xyz-456",
                "model": "gpt-3.5-turbo",
                "completion": {
                    "id": "abc123",
                    "choices": [{
                        "finish_reason": "stop",
                        "index": 0,
                        "logprobs": {"logprobs": "sample logprobs"},
                        "message": {
                            "content": "This is a sample message content.",
                            "refusal": "Sample refusal message.",
                            "role": "assistant"
                        }
                    }],
                    "created": 1633046400,
                    "model": "gpt-3.5-turbo",
                    "object": "text_completion",
                    "system_fingerprint": "fingerprint123",
                    "usage": {
                        "completion_tokens": 50,
                        "prompt_tokens": 100,
                        "total_tokens": 150,
                        "started": 1633046400,
                        "ended": 1633046400
                    }
                }
            }
        }
    )
