from sqlalchemy import Column, String, Integer, Boolean, ARRAY, TIMESTAMP, func
from sqlalchemy.dialects.postgresql import UUID
import uuid
from server.app.db.base import Base  # Adjust the import path as needed
from sqlalchemy.dialects.postgresql import JSONB
from fastapi.encoders import jsonable_encoder

class Gripsbox(Base):
    __tablename__ = "gripsbox"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user = Column(UUID(as_uuid=True), default=uuid.uuid4, nullable=False)
    name = Column(String, nullable=False)
    size = Column(Integer, nullable=False)
    type = Column(String, nullable=False)
    active = Column(Boolean, nullable=False)
    tags = Column(JSONB, nullable=False)
    models = Column(JSONB, nullable=False)
    created = Column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)
    updated = Column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)

    def set_tags(self, data):
        self.context_tags = jsonable_encoder(data)

    def get_tags(self):
        return self.tags

    def set_models(self, data):
        self.models = jsonable_encoder(data)

    def get_models(self):
        return self.tags