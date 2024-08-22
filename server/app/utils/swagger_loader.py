import os
import logging

class SwaggerLoader:

    def __init__(self, file_name: str):
        self.file_name=file_name
        self.logger = logging.getLogger(__name__)

    def file_path(self):
        try:
            from server.app.config.base_config import BaseConfig

            swagger_file_path = os.path.abspath(
                os.path.join(os.path.dirname(__file__),'..','..','..','infrastructure','swagger','swagger.yaml')
            )

            if not os.path.exists(swagger_file_path):
                raise FileNotFoundError(f"File {swagger_file_path} does not exist")

            self.logger.debug(f"SwaggerFile {swagger_file_path} loaded")

            return swagger_file_path

        except Exception as e:
            self.logger.debug(f"Failed to load swaggerFile. Error: {e}")

