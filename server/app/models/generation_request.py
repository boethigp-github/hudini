from pydantic import BaseModel, Field, validator
from typing import List
from enum import Enum

class ModelCategory(str, Enum):
    TEXT_COMPLETION = "text_completion"
    IMAGE_GENERATION = "image_generation"
    AUDIO = "audio"
    EMBEDDING = "embedding"
    MODERATION = "moderation"
    GPT_BASE = "gpt_base"

class Platform(str, Enum):
    OPENAI = "openai"

class ModelConfig(BaseModel):
    id: str = Field(..., description="The ID of the model, which should match the model name.")
    platform: Platform = Platform.OPENAI
    model: str = Field(..., description="The name of the model to be used.")
    temperature: float = Field(default=0.7, ge=0.0, le=1.0)
    max_tokens: int = Field(default=100, ge=1)
    object: str
    category: ModelCategory
    description: str

    @validator('id', pre=True, always=True)
    def set_id_from_model(cls, value, values):
        if not value:
            model = values.get('model')
            if model:
                return model
            raise ValueError("Model field must be provided")
        return value

    class Config:
        use_enum_values = True

class GenerationRequest(BaseModel):
    models: List[ModelConfig] = Field(
        ...,
        min_items=1,
        description="List of models to use for generation",
        example=[
            {
                "id": "gpt-3.5-turbo",
                "platform": "openai",
                "model": "gpt-3.5-turbo",
                "temperature": 0.7,
                "max_tokens": 100,
                "object": "chat.completion",
                "category": "text_completion",
                "description": "A language model for text completions"
            }
        ]
    )
    prompt: str = Field(
        ...,
        min_length=1,
        description="The prompt for generation",
        example="Write a rant in the style of Linus Torvalds about using spaces instead of tabs for indentation in code."
    )
    id: int = Field(
        ...,
        description="Unique identifier for the prompt",
        example=550840021444400000  # Example of a bigint
    )
    method_name: str = Field(
        "fetch_completion",
        description="Method to use for generation",
        example="chat_completion"
    )

    class Config:
        use_enum_values = True
