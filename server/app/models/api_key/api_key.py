from sqlalchemy import Column, String, Boolean, ForeignKey, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from server.app.db.base import Base
from datetime import datetime
import uuid

class ApiKey(Base):
    __tablename__ = 'api_keys'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user = Column(UUID(as_uuid=True), ForeignKey('users.uuid', ondelete='CASCADE'), nullable=False)  # This should match your table definition
    key = Column(String(64), nullable=False)
    created = Column(DateTime, default=datetime.utcnow, nullable=False)
    active = Column(Boolean, default=False, nullable=False)

    # Define the relationship back to User
    user_relationship = relationship("User", back_populates="api_keys")

    @staticmethod
    def get_class_name():
        return "ApiKey"