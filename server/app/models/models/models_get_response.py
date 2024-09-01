from pydantic import BaseModel, Field, ConfigDict
from typing import Optional

class ModelGetResponseModel(BaseModel):
    id: str = Field(..., description="The unique identifier for the model.")
    object: str = Field(..., description="The type of the object, usually 'model'.")
    model: str = Field(..., description="The name of the model.")
    created: int = Field(..., description="The timestamp when the model was created.")
    owned_by: str = Field(..., description="The owner of the model.")
    permission: Optional[str] = Field(None, description="Permissions associated with the model.")
    root: Optional[str] = Field(None, description="Root model if applicable.")
    parent: Optional[str] = Field(None, description="Parent model if applicable.")
    category: str = Field(..., description="The category of the model, e.g., 'text_completion'.")
    description: str = Field(..., description="A description of the model.")
    platform: str = Field(..., description="The platform where the model is available, e.g., 'openai'.")

    # Example usage
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
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
    )
