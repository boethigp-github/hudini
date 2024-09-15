from sqlalchemy import Column, String, Boolean, TIMESTAMP, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid
from server.app.db.base import Base  # Passe den Importpfad ggf. an

class ApiKey(Base):
    __tablename__ = "api_keys"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False)
    user = Column(UUID(as_uuid=True), ForeignKey("users.uuid", ondelete="CASCADE"), nullable=False)
    key = Column(String(64), nullable=False)
    created = Column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)
    active = Column(Boolean, nullable=False, default=False)
