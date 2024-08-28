import os
import json
import logging
from dotenv import load_dotenv


class Settings:
    def __init__(self, config_file=None):
        # Load environment variables from .env.local
        env_path = os.path.join(os.path.dirname(__file__), '../../../infrastructure/environment/.env.local')
        load_dotenv(env_path)  # Load the variables from the .env.local file

        self.log_all_env_variables()
        if config_file is None:
            config_file = os.path.join(os.path.dirname(__file__), 'settings.json')

        with open(config_file, 'r') as f:
            self.config = json.load(f)

        # Resolve placeholders in the config
        self.resolved_config = self.resolve_placeholders(self.config)

    def resolve_placeholders(self, config):
        resolved = {}
        for key, value in config.items():
            if isinstance(value, str):
                resolved[key] = self.resolve_env_variable(value)
            elif isinstance(value, dict):
                resolved[key] = self.resolve_placeholders(value)
            else:
                resolved[key] = value
        return resolved

    def resolve_env_variable(self, value):
        logging.debug(f"Attempting to resolve value: {value}")

        if value.startswith('env:'):
            env_var = value[4:]
            resolved_value = os.getenv(env_var)
            logging.debug(f"Mapping 'env:{env_var}' to environment variable '{env_var}' with value '{resolved_value}'")

            if resolved_value is None:
                raise EnvironmentError(f"Environment variable {env_var} is not set.")
            return resolved_value

        return value

    def log_all_env_variables(self):
        logging.debug("Logging all environment variables:")
        for key, value in os.environ.items():
            logging.debug(f"ENV {key}: {value}")

    def __getattr__(self, item):
        if item in self.resolved_config:
            return self.resolved_config[item]
        raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{item}'")

    def get(self, item, default=None):
        keys = item.split('.')
        value = self.resolved_config
        for key in keys:
            if isinstance(value, dict):
                value = value.get(key, default)
            else:
                return default
        return value

    def items(self):
        return self.resolved_config.items()


# Initialize logging
logging.basicConfig(level=logging.DEBUG)

# Example usage
if __name__ == "__main__":
    # Initialize settings
    settings = Settings()

    # Logging the final resolved configuration for debugging purposes
    logging.debug(f"Final resolved configuration: {settings.resolved_config}")
