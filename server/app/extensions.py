# app/extensions.py
from flask_sqlalchemy import SQLAlchemy
from diskcache import Cache
import os
db = SQLAlchemy()



class FlaskCache:
    def __init__(self, app=None):
        self.cache = None
        if app is not None:
            self.init_cache(app)

    def init_cache(self, app):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        cache_directory = os.path.join(current_dir, '..', 'server', 'var', 'cache')
        app.logger.debug(f"Cache dir setup: {cache_directory}")
        os.makedirs(cache_directory, exist_ok=True)
        self.cache = Cache(cache_directory)
        app.extensions['cache'] = self

    def get(self, key):
        return self.cache.get(key)

    def set(self, key, value, expire=None):
        return self.cache.set(key, value, expire=expire)

cache = FlaskCache()