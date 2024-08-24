import time
import uuid
from typing import Dict, Any
from flask import current_app

class SchemaToModelBuilder:
    def __init__(self, schema: Dict[str, Any]):
        self.schema = schema

    def create_object(self, **kwargs) -> Dict[str, Any]:
        response = {}
        for key, value in self.schema.items():
            if key in kwargs:
                response[key] = kwargs[key]
            elif isinstance(value, dict) and value.get('type') == 'string':  # Check if value is a dict
                response[key] = self._handle_string_type(key, value)
            elif isinstance(value, dict) and value.get('type') == 'number':
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
