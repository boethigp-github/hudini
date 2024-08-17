from app.utils.app_factory import FlaskAppFactory
import sys
import os

# Add the backend directory to the system path so Python can find the app module
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
def create_app():
    # Instanziiere die FlaskAppFactory-Klasse
    factory = FlaskAppFactory()

    # Verwende die Factory, um die Flask-App zu erstellen
    app = factory.create_app()

    return app
