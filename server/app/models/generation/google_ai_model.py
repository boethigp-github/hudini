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
    GOOGLE = "google"
    STREAM_URL = "/stream/google-ai"

class GoogleAIModel(BaseModel):
    id: str
    object: str = "model"  # Google AI models are always of type "model"
    model: str  # This field is required and must be present in the data
    created: int = Field(default_factory=lambda: int(datetime.utcnow().timestamp()))
    owned_by: str = "google"  # All models are owned by Google
    permission: Optional[List[str]] = None
    root: Optional[str] = None
    parent: Optional[str] = None
    category: Optional[ModelCategory] = Field(default=None)
    description: str = "No description provided"
    platform: Platform = Platform.GOOGLE  # Default platform is Google
    stream_url: str = Field(default=Platform.STREAM_URL.value)

    @classmethod
    def from_dict(cls, model_dict: dict):
        """
        Factory method to create a GoogleAIModel instance from a dictionary, with automatic category assignment.
        """
        model = model_dict.get("model", "")
        category = cls.classify_model(model)
        platform = cls.determine_platform(model)
        return cls(
            **model_dict,
            category=category,
            platform=platform,
            description=model_dict.get("description", f"Google AI model {model} categorized as {category.value}, available on {platform.value}")
        )

    @staticmethod
    def classify_model(model: str) -> ModelCategory:
        """
        Classifies the Google AI model based on its ID into a specific category.

        Args:
            model (str): The ID of the model.

        Returns:
            ModelCategory: The category of the model.
        """
        if "chat" in model:
            return ModelCategory.CHAT
        elif "text" in model:
            return ModelCategory.TEXT_COMPLETION
        elif "embed" in model:
            return ModelCategory.EMBEDDING
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
        return Platform.GOOGLE

    model_config = ConfigDict(
        use_enum_values=True  # Ensures that the enum is serialized as a string in the JSON output
    )
