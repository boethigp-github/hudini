from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from typing import Optional

class PromptPostRequestModel(BaseModel):
    prompt: str = Field(..., description="The text of the prompt")
    user: int = Field(..., description="The ID of the user associated with the prompt")
    status: Optional[str] = Field(None, description="The status of the prompt, if applicable")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="The time the prompt was created")

    model_config = ConfigDict(from_attributes=True)
