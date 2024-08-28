import os
import logging
import yaml
from fastapi import HTTPException

class SwaggerLoader:
    """
    SwaggerLoader is a utility class responsible for loading a Swagger YAML file from a specified location.
    It provides methods to retrieve the absolute file path of the Swagger file, load its definition,
    and get specific component schemas.

    Attributes:
        file_name (str): The name of the Swagger YAML file to be loaded.
        logger (logging.Logger): Logger instance for logging debug information.
    """

    def __init__(self, file_name: str, app_logger: logging.Logger = None):
        """
        Initializes the SwaggerLoader instance.

        Args:
            file_name (str): The name of the Swagger YAML file.
            app_logger (logging.Logger): An optional logger instance to be used by the loader.
                                         If not provided, a new logger is created.
        """
        self.file_name = file_name
        self.logger = app_logger or logging.getLogger(__name__)

    def file_path(self) -> str:
        """
        Constructs the absolute path to the Swagger YAML file.

        The method calculates the path to the Swagger file based on the current file's directory.
        It checks if the file exists at the computed path. If the file is not found, an HTTPException is raised.

        Returns:
            str: The absolute path to the Swagger YAML file.

        Raises:
            HTTPException: If the file does not exist at the computed path.
        """
        try:
            # Construct the path to the Swagger YAML file
            swagger_file_path = os.path.abspath(
                os.path.join(os.path.dirname(__file__), '..', '..', '..', 'infrastructure', 'swagger', self.file_name)
            )

            # Check if the file exists
            if not os.path.exists(swagger_file_path):
                self.logger.error(f"File {swagger_file_path} does not exist")
                raise HTTPException(status_code=404, detail=f"Swagger file {self.file_name} not found")

            self.logger.debug(f"SwaggerFile {swagger_file_path} loaded successfully")

            return swagger_file_path

        except Exception as e:
            # Log any exceptions that occur during file path construction
            self.logger.error(f"Failed to load SwaggerFile. Error: {e}")
            raise HTTPException(status_code=500, detail=f"Failed to load Swagger file {self.file_name}")

    def load_definition(self) -> dict:
        """
        Loads the Swagger YAML file and parses it into a Python dictionary.

        Returns:
            dict: The parsed YAML file as a Python dictionary.
        """
        try:
            with open(self.file_path(), 'r') as file:
                definition = yaml.safe_load(file)
                self.logger.debug("Swagger definition loaded successfully")
                return definition
        except Exception as e:
            self.logger.error(f"Failed to load the Swagger definition. Error: {e}")
            raise HTTPException(status_code=500, detail="Failed to load Swagger definition")

    def get_component_schema(self, component_name: str) -> dict:
        """
        Retrieves a specific component schema from the Swagger definition.

        Args:
            component_name (str): The name of the component schema to retrieve.

        Returns:
            dict: The component schema as a Python dictionary.

        Raises:
            HTTPException: If the component schema is not found.
        """
        try:
            definition = self.load_definition()
            schema = definition['components']['schemas'].get(component_name)
            if not schema:
                raise KeyError(f"Component schema '{component_name}' not found")
            self.logger.debug(f"Component schema '{component_name}' retrieved successfully")
            return schema
        except KeyError as e:
            self.logger.error(str(e))
            raise HTTPException(status_code=404, detail=str(e))
        except Exception as e:
            self.logger.error(f"Failed to retrieve component schema. Error: {e}")
            raise HTTPException(status_code=500, detail=f"Failed to retrieve component schema '{component_name}'")
