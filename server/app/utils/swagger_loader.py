import os
import logging

class SwaggerLoader:

    def __init__(self, file_name: str):
        self.file_name=file_name
        self.logger = logging.getLogger(__name__)

    def file_path(self):
        try:
            from server.app.config.base_config import BaseConfig

            file_path = os.path.dirname(os.path.abspath(__file__))

            if not os.path.exists(file_path):
                raise FileNotFoundError(f"File {file_path} does not exist")

            self.logger.debug(f"SwaggerFile {file_path} loaded")

            return file_path

        except Exception as e:
            self.logger.debug(f"Failed to load swaggerFile. Error: {e}")

