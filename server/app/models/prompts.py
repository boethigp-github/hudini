# models/prompt.py

from sqlalchemy import Column, String, DateTime, Text
from sqlalchemy.dialects.postgresql import UUID
import uuid
from datetime import datetime
from ..db.base import Base  # Import Base from the shared module

# SQLAlchemy model
class Prompt(Base):  # Use the Base directly
    __tablename__ = 'prompts'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    prompt = Column(Text, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    user = Column(String(30), nullable=False)
    status = Column(String(30), nullable=False)

    def to_dict(self):
        return {
            "id": str(self.id),
            "prompt": self.prompt,
            "timestamp": self.timestamp.isoformat(),
            "user": self.user,
            "status": self.status
        }
