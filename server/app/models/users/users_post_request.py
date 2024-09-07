from pydantic import BaseModel, Field, ConfigDict
from typing import Optional

class UserPostRequestModel(BaseModel):
    username: str = Field(..., description="The name of the user")
    email: str = Field(..., description="The email address of the user")

    # Updated for Pydantic v2
    model_config = ConfigDict(from_attributes=True)