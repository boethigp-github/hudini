import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from server.app.factory.app_factory import FlaskAppFactory
from server.app.config.base_config import BaseConfig
import os

app = FlaskAppFactory().create_app(BaseConfig)

if __name__ == "__main__":
    debug =BaseConfig.FLASK_DEBUG
    app.logger.debug(f'DEBUG: {debug}')
    app.logger.debug(f'FLASK_ENV: {os.getenv("FLASK_ENV")}')
    app.logger.debug(f'FLASK_DEBUG: {os.getenv("FLASK_DEBUG")}')
    app.run(debug=debug)