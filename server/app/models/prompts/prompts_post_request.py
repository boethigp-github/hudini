from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from typing import Optional

class PromptPostRequestModel(BaseModel):
    prompt: str = Field(..., description="The text of the prompt")
    user: int = Field(..., description="The ID of the user associated with the prompt")
    status: Optional[str] = Field(None, description="The status of the prompt, if applicable")


    model_config = ConfigDict(from_attributes=True)
