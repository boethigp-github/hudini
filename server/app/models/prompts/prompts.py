import uuid
from sqlalchemy import Column, BigInteger, Text, DateTime, String
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
from server.app.db.base import Base

class Prompt(Base):
    __tablename__ = 'prompts'

    prompt = Column(Text, nullable=False)
    user = Column(UUID(as_uuid=True), nullable=False)  # UUID should be passed explicitly
    status = Column(String(50), nullable=False)  # Use String for flexibility
    created = Column(DateTime, default=datetime.utcnow)
    uuid = Column(UUID(as_uuid=True), nullable=False, primary_key=True)  # No default, must be provided from the request

    def to_dict(self):
        """Converts the model instance to a dictionary with correct formatting."""
        return {
            "prompt": self.prompt,
            "user": self.user,
            "status": self.status,
            # Convert created to a Unix timestamp
            "created": int(self.created.timestamp()),
            "uuid": str(self.uuid)
        }
