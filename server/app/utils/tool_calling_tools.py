
import logging
import json
from server.app.services.user_service import UserService
from sqlalchemy.future import select
from server.app.models.users.user import User
logger = logging.getLogger(__name__)
import httpx
def get_tool_calling_tools():
    return [
        {
            "name": "get_weather",
            "description": "Fetches the weather for a given location.",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {"type": "string", "description": "City name for the weather."},
                    "unit": {"type": "string", "enum": ["Celsius", "Fahrenheit"], "default": "Celsius"},
                },
                "required": ["location"],
            },
        },
        {
            "name": "get_hudini_user",
            "description": "Provides information about the Hudini user.",

        },
    ]

def get_weather(location: str, unit: str = "Celsius") -> str:
    """
    Fetch real-time weather data using wttr.in (synchronous).

    Args:
        location (str): The city name to fetch the weather for.
        unit (str): The temperature unit (Celsius or Fahrenheit).

    Returns:
        str: A formatted string with the weather details.
    """
    unit_mapping = {"Celsius": "m", "Fahrenheit": "u"}
    unit_param = unit_mapping.get(unit, "m")  # Default to Celsius

    url = f"https://wttr.in/{location}?format=%C+%t&{unit_param}&lang=de"

    try:
        response = httpx.get(url)
        response.raise_for_status()  # Raise an exception for HTTP errors

        # Get the plain text response
        weather_data = response.text.strip()
        return f"In {location} ist das Wetter aktuell: {weather_data}."
    except httpx.HTTPStatusError as e:
        logger.error(f"HTTP error occurred: {e}")
        return f"Fehler beim Abrufen der Wetterdaten für {location}."
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return f"Ein unerwarteter Fehler ist aufgetreten."

async def get_hudini_user() -> str:
    """
    Retrieves all users and returns them as a JSON string, including the SQL query used.

    Returns:
        str: JSON string containing users and the executed SQL query.
    """
    user_service = UserService()

    # Prepare the SQL query for logging
    query = select(User)
    compiled_query = str(query.compile(compile_kwargs={"literal_binds": True}))

    # Fetch users
    users = await user_service.get_all_users()

    # Include SQL in the response
    response = {
        "users": users,
        "sql": compiled_query
    }

    return json.dumps(response, ensure_ascii=False)