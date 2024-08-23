import time
import uuid
import os
import yaml
from typing import Dict, Any
from flask import current_app


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


