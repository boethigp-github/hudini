from pydantic import BaseModel
from typing import Dict, Any

# Pydantic model for tool call response
class ToolCallResponseModel(BaseModel):
    tool: str  # The name of the tool that was called
    result: Dict[str, Any]  # The result of the tool call, can include various data depending on the tool

    class ConfigDict:
        json_schema_extra = {
            "example": {
                "tool": "get_weather",
                "result": {
                    "message": "Weather data for Berlin",
                    "data": {
                        "location": "Berlin",
                        "temperature": "18°C",
                        "condition": "Clear skies",
                        "humidity": "50%",
                        "wind_speed": "10 km/h"
                    }
                }
            }
        }
