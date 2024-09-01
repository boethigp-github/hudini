import uuid
from sqlalchemy import Column, BigInteger, String, Text, DateTime
from sqlalchemy.dialects.postgresql import UUID  # Import the UUID type for PostgreSQL
from datetime import datetime
from server.app.db.base import Base

def get_current_timestamp():
    return int(datetime.utcnow().timestamp())

class Prompt(Base):
    __tablename__ = 'prompts'

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    prompt = Column(Text, nullable=False)
    user = Column(BigInteger, nullable=False)
    status = Column(String(30), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    uuid = Column(UUID(as_uuid=True), nullable=False, default=uuid.uuid4)  # Use UUID type

    def to_dict(self):
        return {
            "id": self.id,
            "prompt": self.prompt,
            "user": self.user,
            "status": self.status,
            "created_at": self.created_at.isoformat(),
            "uuid": str(self.uuid)  # Converting UUID to string for JSON serialization
        }
