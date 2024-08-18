import time
import uuid
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
