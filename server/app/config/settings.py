import os
import json
import logging.config


class Settings:
    def __init__(self, config_file=None):
        if config_file is None:
            config_file = os.path.join(os.path.dirname(__file__), 'settings.json')

        with open(config_file, 'r') as f:
            self.config = json.load(f)

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
        if isinstance(value, str) and value.startswith('${') and value.endswith('}'):
            env_var, _, default = value[2:-1].partition(':')
            return os.getenv(env_var, default)
        return value

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


# Initialize settings
settings = Settings()