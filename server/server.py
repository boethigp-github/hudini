from app.utils.app_factory import FlaskAppFactory
from app.config import Config
import os
app_factory = FlaskAppFactory()
app = app_factory.create_app(Config)

# Error handler for all exceptions
@app.errorhandler(Exception)
def handle_exception(e):
    # Log the exception
    app.logger.exception('An unhandled exception occurred')
    # Return a custom error page
    return "An unexpected error occurred", 500

if __name__ == "__main__":
    debug =Config.FLASK_DEBUG
    app.logger.debug(f'DEBUG: {debug}')
    app.logger.debug(f'FLASK_ENV: {os.getenv("FLASK_ENV")}')
    app.logger.debug(f'FLASK_DEBUG: {os.getenv("FLASK_DEBUG")}')
    app.run(debug=debug)