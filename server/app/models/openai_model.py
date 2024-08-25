from pydantic import BaseModel, Field, ConfigDict
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


class OpenAIModel(BaseModel):
    id: str
    object: str
    created: Optional[int] = None
    owned_by: Optional[str] = None
    permission: Optional[List[str]] = None
    root: Optional[str] = None
    parent: Optional[str] = None
    category: Optional[ModelCategory] = Field(default=None)
    description: Optional[str] = None  # A brief description of the model's purpose
    platform: Platform = Platform.OPENAI  # Default platform is OpenAI

    @classmethod
    def from_dict(cls, model_dict: dict):
        """
        Factory method to create an OpenAIModel instance from a dictionary, with automatic category assignment.
        """
        model_id = model_dict.get("id", "")
        category = cls.classify_model(model_id)
        platform = cls.determine_platform(model_id)
        return cls(
            **model_dict,
            category=category,
            platform=platform,
            description=f"Model {model_id} categorized as {category.value}, available on {platform.value}"
        )

    @staticmethod
    def classify_model(model_id: str) -> ModelCategory:
        """
        Classifies the model based on its ID into a specific category.

        Args:
            model_id (str): The ID of the model.

        Returns:
            ModelCategory: The category of the model.
        """
        if "gpt" in model_id or "davinci" in model_id or "curie" in model_id or "babbage" in model_id:
            return ModelCategory.TEXT_COMPLETION
        elif "embedding" in model_id or "ada" in model_id:
            return ModelCategory.EMBEDDING
        elif "dall-e" in model_id:
            return ModelCategory.IMAGE_GENERATION
        elif "whisper" in model_id:
            return ModelCategory.AUDIO
        elif "tts" in model_id:
            return ModelCategory.AUDIO
        elif "moderation" in model_id:
            return ModelCategory.MODERATION
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

        return Platform.OPENAI  # Default to OpenAI for standard models

    model_config = ConfigDict(
        use_enum_values=True  # Ensures that the enum is serialized as a string in the JSON output
    )