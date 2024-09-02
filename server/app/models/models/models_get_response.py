from pydantic import BaseModel, Field, ConfigDict
from typing import Optional

class ModelGetResponseModel(BaseModel):
    id: str = Field("default-id", description="The unique identifier for the model.")
    object: str = Field("model", description="The type of the object, usually 'model'.")
    model: str = Field("default-model", description="The name of the model.")
    owned_by: str = Field("system", description="The owner of the model.")
    permission: Optional[str] = Field(None, description="Permissions associated with the model.")
    root: Optional[str] = Field(None, description="Root model if applicable.")
    parent: Optional[str] = Field(None, description="Parent model if applicable.")
    category: str = Field("default-category", description="The category of the model, e.g., 'text_completion'.")
    description: str = Field("Default description of the model.", description="A description of the model.")
    platform: str = Field("default-platform", description="The platform where the model is available, e.g., 'openai'.")

    # Config class for default settings
    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": "gpt-4o-2024-05-13",
                "object": "model",
                "model": "gpt-4o-2024-05-13",
                "created": 1715368132,
                "owned_by": "system",
                "permission": None,
                "root": None,
                "parent": None,
                "category": "text_completion",
                "description": "Model gpt-4o-2024-05-13 categorized as text_completion, available on openai",
                "platform": "openai"
            }
        }
