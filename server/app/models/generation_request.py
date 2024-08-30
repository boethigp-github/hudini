from pydantic import BaseModel, Field, model_validator
from typing import Optional, List
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
    model: str
    temperature: Optional[float] = Field(default=0.7, ge=0.0, le=1.0)
    max_tokens: Optional[int] = Field(default=100, ge=1)
    model_id: Optional[str] = None
    object: str
    category: Optional[ModelCategory] = None
    description: Optional[str] = None

    @model_validator(mode='before')
    def set_id_from_model(cls, values):
        model = values.get('model')
        if not model:
            raise ValueError("Model field must be provided")
        if not values.get('id'):
            values['id'] = model
        return values

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
                "model_id": None,
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
    prompt_id: str = Field(
        ...,
        min_length=1,
        description="Unique identifier for the prompt",
        example="550e8400-e29b-41d4-a716-446655440000"
    )
    method_name: str = Field(
        "fetch_completion",
        description="Method to use for generation",
        example="chat_completion"
    )

    class Config:
        use_enum_values = True
