from pydantic import BaseModel
from uuid import UUID
from datetime import datetime

class GripsboxPostResponseModel(BaseModel):
    id: UUID
    name: str
    size: int
    type: str
    active: bool
    tags: list[str]
    created: datetime  # Use datetime if handling date formats
    updated: datetime  # Same as above

    class Config:
        json_encoders = {
            UUID: lambda v: str(v)  # Automatically serialize UUIDs to strings
        }
        from_attributes = True  # Enable from_orm method

    @classmethod
    def from_orm(cls, obj):
        """Convert an ORM object to a Pydantic model."""
        return cls(
            id=obj.id,
            name=obj.name,
            size=obj.size,
            type=obj.type,
            active=obj.active,
            tags=obj.tags,
            created=obj.created,
            updated=obj.updated
        )
