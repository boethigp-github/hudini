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
    STREAM_URL = "/stream/anthropic"

class AnthropicModel(BaseModel):
    id: str
    object: str = "model"  # Anthropic models are always of type "model"
    model: str  # This field is required and must be present in the data
    created: int = Field(default_factory=lambda: int(datetime.utcnow().timestamp()))
    owned_by: str = "anthropic"  # All models are owned by Anthropic
    permission: Optional[List[str]] = None
    root: Optional[str] = None
    parent: Optional[str] = None
    category: Optional[ModelCategory] = Field(default=None)
    description: str = "No description provided"
    platform: Platform = Platform.ANTHROPIC  # Default platform is Anthropic
    stream_url: str = Field(default=Platform.STREAM_URL.value)

    @classmethod
    def from_dict(cls, model_dict: dict):
        """
        Factory method to create an AnthropicModel instance from a dictionary, with automatic category assignment.
        """
        model = model_dict.get("model", "")
        category = cls.classify_model(model)
        platform = cls.determine_platform(model)
        return cls(
            **model_dict,
            category=category,
            platform=platform,
            description=model_dict.get("description", f"Anthropic model {model} categorized as {category.value}, available on {platform.value}")
        )

    @staticmethod
    def classify_model(model: str) -> ModelCategory:
        """
        Classifies the Anthropic model based on its ID into a specific category.

        Args:
            model (str): The ID of the model.

        Returns:
            ModelCategory: The category of the model.
        """
        if model.startswith("claude-3"):
            return ModelCategory.CHAT
        elif model.startswith("claude-2") or model.startswith("claude-instant"):
            return ModelCategory.TEXT_COMPLETION
        else:
            return ModelCategory.GPT_BASE  # Default or fallback category

    @staticmethod
    def determine_platform(model: str) -> Platform:
        """
        Determines the platform based on the model ID.

        Args:
            model (str): The ID of the model.

        Returns:
            Platform: The platform where the model is available.
        """
        return Platform.ANTHROPIC

    model_config = ConfigDict(
        use_enum_values=True  # Ensures that the enum is serialized as a string in the JSON output
    )
