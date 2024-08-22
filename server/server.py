import sys
import os
from flask import jsonify
# Assuming your script is being run from inside the server directory
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.utils.app_factory import FlaskAppFactory
from server.app.config.base_config import BaseConfig
import os
app_factory = FlaskAppFactory()
app = app_factory.create_app(BaseConfig)

# Error handler for all exceptions
@app.errorhandler(Exception)
def handle_exception(e):
    # Log the exception
    app.logger.exception('An unhandled exception occurred')
    # Return a custom error page
    response = jsonify({'error': str(e)})
    response.status_code = 500
    return response

if __name__ == "__main__":
    debug =BaseConfig.FLASK_DEBUG
    app.logger.debug(f'DEBUG: {debug}')
    app.logger.debug(f'FLASK_ENV: {os.getenv("FLASK_ENV")}')
    app.logger.debug(f'FLASK_DEBUG: {os.getenv("FLASK_DEBUG")}')
    app.run(debug=debug)