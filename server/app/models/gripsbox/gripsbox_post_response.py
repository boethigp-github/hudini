from pydantic import BaseModel
from uuid import UUID
from datetime import datetime

class GripsboxPostResponseModel(BaseModel):
    id: UUID
    user: UUID
    name: str
    size: int
    type: str
    active: bool
    tags: list[str]
    models: list[str]
    created: datetime
    updated: datetime

    class Config:
        json_encoders = {
            UUID: lambda v: str(v)  # Automatically serialize UUIDs to strings
        }
        from_attributes = True

    @classmethod
    def from_orm(cls, obj):
        """Convert an ORM object to a Pydantic model."""
        return cls(
            id=obj.id,
            user=obj.user,
            name=obj.name,
            size=obj.size,
            type=obj.type,
            active=obj.active,
            tags=obj.tags,
            models=obj.models,
            created=obj.created,
            updated=obj.updated
        )
