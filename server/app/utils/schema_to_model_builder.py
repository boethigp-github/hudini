import time
import uuid
import os
import yaml
from typing import Dict, Any

class SchemaToModelBuilder:
    def __init__(self, schema: Dict[str, Any]):
        self.schema = schema

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

    def load_swagger_definition() -> Dict[str, Any]:
        swagger_yaml_path = os.path.join(os.path.dirname(__file__), '..', '..', 'swagger.yaml')
        try:
            with open(swagger_yaml_path, 'r') as file:
                return yaml.safe_load(file)
        except FileNotFoundError:
            logger.error(f"Swagger file not found at {swagger_yaml_path}")
            raise
        except yaml.YAMLError as e:
            logger.error(f"Error parsing Swagger YAML: {e}")
            raise
