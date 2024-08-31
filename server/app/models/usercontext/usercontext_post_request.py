from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from uuid import UUID

class UserContextPostRequestModel(BaseModel):
    user_id: UUID
    thread_id: int
    context_data: Optional[Dict[str, Any]] = None