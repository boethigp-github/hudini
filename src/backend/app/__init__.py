from app.utils.app_factory import FlaskAppFactory

def create_app():
    # Instanziiere die FlaskAppFactory-Klasse
    factory = FlaskAppFactory()

    # Verwende die Factory, um die Flask-App zu erstellen
    app = factory.create_app()

    return app
