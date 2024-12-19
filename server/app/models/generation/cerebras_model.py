from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from enum import Enum

class ModelCategory(str, Enum):
    TEXT_COMPLETION = "text_completion"

class Platform(str, Enum):
    CEREBRAS = "cerebras"
    STREAM_URL = "/stream/cerebras"

class CerebrasModel(BaseModel):
    id: str
    object: str
    model: str  # Dieses Feld ist erforderlich und muss in den Daten vorhanden sein
    created: Optional[int] = None
    owned_by: Optional[str] = None
    permission: Optional[List[str]] = None
    root: Optional[str] = None
    parent: Optional[str] = None
    category: Optional[ModelCategory] = Field(default=None)
    description: Optional[str] = None
    platform: Platform = Platform.CEREBRAS
    stream_url: str = Field(default=Platform.STREAM_URL.value)

    @classmethod
    def from_dict(cls, model_dict: dict):
        """
        Factory method to create an OpenAIModel instance from a dictionary, with automatic category assignment.
        """
        model = model_dict.get("model", "")
        category = cls.classify_model(model)
        platform = cls.determine_platform(model)

        # Prüfen, ob das model-Feld vorhanden ist, wenn nicht, setze es auf model_id oder ein anderes Feld
        if "model" not in model_dict:
            model_dict["model"] = model  # Setze 'model' auf die ID, wenn kein 'model' Feld vorhanden ist

        return cls(
            **model_dict,
            category=category,
            platform=platform,
            description=f"Model {model} categorized as {category.value}, available on {platform.value}"
        )

    @staticmethod
    def classify_model(model: str) -> ModelCategory:
        """
        Classifies the model based on its ID into a specific category.

        Args:
            model (str): The ID of the model.

        Returns:
            ModelCategory: The category of the model.
        """

        return ModelCategory.TEXT_COMPLETION

    @staticmethod
    def determine_platform(model: str) -> Platform:
        """
        Determines the platform based on the model ID.

        Args:
            model (str): The ID of the model.

        Returns:
            Platform: The platform where the model is available.
        """

        return Platform.CEREBRAS  # Default to OpenAI for standard models

    model_config = ConfigDict(
        use_enum_values=True  # Ensures that the enum is serialized as a string in the JSON output
    )
