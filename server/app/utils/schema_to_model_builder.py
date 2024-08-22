import time
import uuid
import os
import yaml
from typing import Dict, Any

from flask import current_app

from server.app.utils.swagger_loader import SwaggerLoader


class SchemaToModelBuilder:
    def __init__(self, schema: Dict[str, Any]):
        self.schema = schema
        self.logger = current_app.logger

    def create_object(self, **kwargs) -> Dict[str, Any]:
        response = {}
        for key, value in self.schema.items():
            if key in kwargs:
                response[key] = kwargs[key]
            elif value.get('type') == 'string':
                response[key] = self._handle_string_type(key, value)
            elif value.get('type') == 'number':
                response[key] = 0
            else:
                response[key] = None
        return response

    def _handle_string_type(self, key: str, value: Dict[str, Any]) -> str:
        if key == 'timestamp':
            return time.strftime('%Y-%m-%d %H:%M:%S')
        elif value.get('format') == 'uuid':
            return str(uuid.uuid4())
        else:
            return ''

    @classmethod
    def from_swagger_definition(cls, swagger_def: Dict[str, Any], schema_name: str):
        schema = swagger_def['components']['schemas'][schema_name]['properties']
        return cls(schema)

    @classmethod
    def load_swagger_definition(cls) -> Dict[str, Any]:

        from server.app.utils.swagger_loader import SwaggerLoader
        swagger_yaml_path = SwaggerLoader("swagger.yaml").file_path()

        try:
            with open(swagger_yaml_path, 'r') as file:
                return yaml.safe_load(file)
        except FileNotFoundError:
            self.logger.error(f"Swagger file not found at {swagger_yaml_path}")
            raise
        except yaml.YAMLError as e:
            self.logger.error(f"Error parsing Swagger YAML: {e}")
            raise
