from pydantic import BaseModel, Field
from typing import Optional, Dict, Any,Union

class ErrorDetail(BaseModel):
    message: str
    type: str
    param: str
    code: Optional[Any] = None

class ErrorModel(BaseModel):
    error: ErrorDetail

class ErrorGenerationModel(BaseModel):
    model: str
    error: Union[str, ErrorModel]