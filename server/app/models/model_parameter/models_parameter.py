import uuid
from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, JSON
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from datetime import datetime
from server.app.db.base import Base


class ModelParameter(Base):
    __tablename__ = 'model_parameter'

    uuid = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user = Column(PG_UUID(as_uuid=True), ForeignKey('users.uuid', ondelete='CASCADE'), nullable=False)
    parameter = Column(String(200), nullable=True)
    model = Column(String(200), nullable=False)
    value = Column(JSON, nullable=False)
    active = Column(Boolean, nullable=False, server_default='FALSE')
    created = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=True)

    def to_dict(self):
        """Converts the model instance to a dictionary for API responses."""
        return {
            "uuid": str(self.uuid),
            "user": str(self.user),
            "parameter": self.parameter,
            "model": self.model,
            "value": self.value,
            "active": self.active,
            "created": self.created.isoformat() if self.created else None,
            "updated": self.updated.isoformat() if self.updated else None,
        }
