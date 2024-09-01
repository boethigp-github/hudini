import uuid
from sqlalchemy import Column, BigInteger, Text, DateTime, String
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
from server.app.db.base import Base

class Prompt(Base):
    __tablename__ = 'prompts'

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    prompt = Column(Text, nullable=False)
    user = Column(BigInteger, nullable=False)
    status = Column(String(50), nullable=False)  # Verwende String anstelle von Enum
    created_at = Column(DateTime, default=datetime.utcnow)
    uuid = Column(UUID(as_uuid=True), nullable=False, default=uuid.uuid4)

    def to_dict(self):
        return {
            "id": self.id,
            "prompt": self.prompt,
            "user": self.user,
            "status": self.status,  # Kein .value nötig, da es ein String ist
            "created_at": self.created_at.isoformat(),
            "uuid": str(self.uuid)
        }
