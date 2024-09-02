from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from enum import Enum
from datetime import datetime

class ModelCategory(str, Enum):
    TEXT_COMPLETION = "text_completion"
    CHAT = "chat"
    EMBEDDING = "embedding"
    GPT_BASE = "gpt_base"

class Platform(str, Enum):
    ANTHROPIC = "anthropic"

class AnthropicModel(BaseModel):
    id: str
    model: str
    object: str = "model"  # Anthropic models are always of type "model"
    owned_by: str = "anthropic"  # All models are owned by Anthropic
    permission: Optional[List[str]] = None
    root: Optional[str] = None
    parent: Optional[str] = None
    category: Optional[ModelCategory] = Field(default=None)
    description: Optional[str] = Field(default="No description provided", description="A description of the model.")
    platform: Platform = Platform.ANTHROPIC  # Default platform is Anthropic

    @staticmethod
    def classify_model(model_id: str) -> ModelCategory:
        """
        Classifies the Anthropic model based on its ID into a specific category.

        Args:
            model_id (str): The ID of the model.

        Returns:
            ModelCategory: The category of the model.
        """
        if model_id.startswith("claude-3"):
            return ModelCategory.CHAT
        elif model_id.startswith("claude-2") or model_id.startswith("claude-instant"):
            return ModelCategory.TEXT_COMPLETION
        else:
            return ModelCategory.GPT_BASE  # Default or fallback category

    @staticmethod
    def determine_platform(model_id: str) -> Platform:
        """
        Determines the platform based on the model ID.

        Args:
            model_id (str): The ID of the model.

        Returns:
            Platform: The platform where the model is available.
        """
        return Platform.ANTHROPIC

    class Config:
        use_enum_values = True  # Ensures that the enum is serialized as a string in the JSON output
