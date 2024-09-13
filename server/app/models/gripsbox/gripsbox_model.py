from sqlalchemy import Column, String, Integer, Boolean, ARRAY, TIMESTAMP, func
from sqlalchemy.dialects.postgresql import UUID
import uuid
from server.app.db.base import Base  # Adjust the import path as needed

class Gripsbox(Base):
    __tablename__ = "gripsbox"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    size = Column(Integer, nullable=False)
    type = Column(String, nullable=False)
    active = Column(Boolean, nullable=False)
    tags = Column(ARRAY(String), nullable=False)
    created = Column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)
    updated = Column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)
