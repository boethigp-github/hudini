import os
import logging
import yaml

class SwaggerLoader:
    """
    SwaggerLoader is a utility class responsible for loading a Swagger YAML file from a specified location.
    It provides a method to retrieve the absolute file path of the Swagger file, ensuring that the file exists.

    Attributes:
        file_name (str): The name of the Swagger YAML file to be loaded.
        logger (logging.Logger): Logger instance for logging debug information.

    Methods:
        file_path() -> str:
            Constructs and returns the absolute path to the Swagger file.
            Raises a FileNotFoundError if the file does not exist.
    """

    def __init__(self, file_name: str):
        """
        Initializes the SwaggerLoader instance.

        Args:
            file_name (str): The name of the Swagger YAML file.

        Initializes the logger and stores the file name for further use.
        """
        self.file_name = file_name
        self.logger = logging.getLogger(__name__)

    def file_path(self) -> str:
        """
        Constructs the absolute path to the Swagger YAML file.

        The method calculates the path to the Swagger file based on the current file's directory.
        It checks if the file exists at the computed path. If the file is not found, a FileNotFoundError is raised.

        Returns:
            str: The absolute path to the Swagger YAML file.

        Raises:
            FileNotFoundError: If the file does not exist at the computed path.
        """
        try:
            from server.app.config.base_config import BaseConfig

            # Construct the path to the Swagger YAML file
            swagger_file_path = os.path.abspath(
                os.path.join(os.path.dirname(__file__), '..', '..', '..', 'infrastructure', 'swagger', self.file_name)
            )

            # Check if the file exists
            if not os.path.exists(swagger_file_path):
                raise FileNotFoundError(f"File {swagger_file_path} does not exist")

            self.logger.debug(f"SwaggerFile {swagger_file_path} loaded")

            return swagger_file_path

        except Exception as e:
            # Log any exceptions that occur during file path construction
            self.logger.debug(f"Failed to load SwaggerFile. Error: {e}")
            raise

    def load_definition(self):
        with open(self.file_path(), 'r') as file:
            return yaml.safe_load(file)

    def get_component_schema(self, component_name):
        return self.load_definition()['components']['schemas'][component_name]