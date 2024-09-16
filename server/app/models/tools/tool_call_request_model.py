from pydantic import BaseModel
from typing import Dict, Any

# Pydantic model for tool call request
class ToolCallRequestModel(BaseModel):
    tool: str  # The name of the tool being called, e.g., "get_weather"
    parameters: Dict[str, Any]  # A dictionary of parameters needed for the tool call

    class Config:
        schema_extra = {
            "example": {
                "tool": "get_weather",
                "parameters": {
                    "location": "Berlin"
                }
            }
        }
