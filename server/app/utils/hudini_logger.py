import logging
import logging.config
from ..config.settings import Settings

# Initialize settings
settings = Settings()

# Resolve the logging configuration from the settings
logging_config = settings.get('default').get('LOGGING_CONFIG')

# Apply the logging configuration
logging.config.dictConfig(logging_config)

# Create and configure the global logger named 'hudini_logger'
hudini_logger = logging.getLogger('hudini_logger')
hudini_logger.debug("Global hudini_logger initialized")
