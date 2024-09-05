import os
import sys
from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context

# Add the project root to sys.path so Python can find 'server'
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../../')))

# Import the synchronous engine and Base from your app
from server.app.db.base import Base, sync_engine
from server.app.config.settings import  Settings

settings = Settings()
# This is the Alembic Config object, which provides access to the values within the .ini file in use.
config = context.config

# Dynamically set the SQLALCHEMY_DATABASE_URL from the environment variable for migrations (sync connection)
SQLALCHEMY_DATABASE_URL = settings.get("default").get("DATABASE_URL_SYNC")

# Set the sqlalchemy.url dynamically
config.set_main_option("sqlalchemy.url", SQLALCHEMY_DATABASE_URL)

# Interpret the config file for Python logging.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Set target_metadata to your models' metadata for autogenerate support
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(url=url, target_metadata=target_metadata, literal_binds=True)

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    connectable = sync_engine  # Using the synchronous engine for migrations

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
