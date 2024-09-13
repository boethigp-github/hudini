import click
from diskcache import FanoutCache
# Ensure the root of the project is in sys.path
import logging
import os,sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../')))
from server.app.config.settings import Settings  # Importing your Settings


# Initialize the logger
logger = logging.getLogger("cache_clear")

@click.command('cache-clear')
def cache_clear():
    """
    CLI command to clear the FanoutCache used in the FastAPI app.
    """
    # Load settings
    settings = Settings()  # Load settings from the environment

    # Get the cache directory from settings
    cache_directory = settings.default["APP_CACHE"]  # Fetch APP_CACHE from settings

    # Initialize FanoutCache with the specified cache directory
    cache = FanoutCache(directory=cache_directory, shards=8)

    # Clear the cache
    logger.debug("Clearing cache...")
    cache.clear()
    click.echo("Cache cleared successfully.")

if __name__ == "__main__":
    cache_clear()
