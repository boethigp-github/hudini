import os
import yaml
import logging.config

class Settings:
    config: dict = None  # Define config as an instance variable

    def __init__(self, **kwargs):
        self.load_yaml_settings()  # Load YAML settings

    def load_yaml_settings(self):
        # Load the configuration from the settings.yaml file
        config_file_path = os.path.join(os.path.dirname(__file__), 'settings.yaml')
        with open(config_file_path, 'r') as file:
            self.config = yaml.safe_load(file)

    def __getattr__(self, item):
        """
        Intercept attribute access to dynamically return configuration values.
        If the attribute doesn't exist in the loaded configuration, raise an AttributeError.
        """
        value = self.get(item)
        if value is not None:
            return value
        raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{item}'")

    def get(self, item, default=None):
        """
        Retrieves the configuration value from the loaded YAML file.
        Supports nested keys separated by '__' (double underscores).
        """
        keys = item.split('__')
        value = self.config
        try:
            for key in keys:
                value = value[key]
            return value
        except KeyError:
            return default
