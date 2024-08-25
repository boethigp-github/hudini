from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from enum import Enum

class ModelCategory(str, Enum):
    TEXT_COMPLETION = "text_completion"
    CHAT = "chat"
    EMBEDDING = "embedding"
    GPT_BASE = "gpt_base"

class Platform(str, Enum):
    ANTHROPIC = "anthropic"


class AnthropicModel(BaseModel):
    id: str
    object: str = "model"  # Anthropic models are always of type "model"
    created: Optional[int] = None
    owned_by: str = "anthropic"  # All models are owned by Anthropic
    permission: Optional[List[str]] = None
    root: Optional[str] = None
    parent: Optional[str] = None
    category: Optional[ModelCategory] = Field(default=None)
    description: Optional[str] = None
    platform: Platform = Platform.ANTHROPIC  # Default platform is Anthropic

    @classmethod
    def from_dict(cls, model_dict: dict):
        """
        Factory method to create an AnthropicModel instance from a dictionary, with automatic category assignment.
        """
        model_id = model_dict.get("id", "")
        category = cls.classify_model(model_id)
        platform = cls.determine_platform(model_id)
        return cls(
            **model_dict,
            category=category,
            platform=platform,
            description=f"Anthropic model {model_id} categorized as {category.value}, available on {platform.value}"
        )

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

    model_config = ConfigDict(
        use_enum_values=True  # Ensures that the enum is serialized as a string in the JSON output
    )