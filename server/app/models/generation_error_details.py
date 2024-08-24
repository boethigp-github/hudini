from pydantic import BaseModel, Field
from typing import Optional, Dict, Any,Union

class GenerationErrorDetail(BaseModel):
    message: str
    type: str
    param: str
    code: Optional[Any] = None

class ErrorModel(BaseModel):
    error: GenerationErrorDetail

class ErrorGenerationModel(BaseModel):
    model: str
    error: Union[str, ErrorModel]