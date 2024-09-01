from sqlalchemy import Column, BigInteger, String, Text, DateTime
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

    def to_dict(self):
        return {
            "id": self.id,
            "prompt": self.prompt,
            "user": self.user,
            "status": self.status,
            "created_at": self.created_at.isoformat(),  # Returning timestamp directly
        }
