from flask_swagger_ui import get_swaggerui_blueprint
from app.config import Config

swaggerui_blueprint = get_swaggerui_blueprint(
    Config.SWAGGER_URL,
    Config.API_URL,
    config={  # Swagger UI config overrides
        'app_name': "Hudini API"
    },
)
