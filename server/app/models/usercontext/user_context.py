from sqlalchemy import Column, Integer, String, DateTime, JSON
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
import uuid
from datetime import datetime
from ...db.base import Base  # Import Base aus dem gemeinsamen Modul

class UserContextModel(Base):
    __tablename__ = 'user_context'  # Tabellenname in der Datenbank

    id = Column(Integer, primary_key=True, autoincrement=True)
    user = Column(PG_UUID(as_uuid=True), nullable=False, default=uuid.uuid4)
    prompt_id = Column(PG_UUID(as_uuid=True), nullable=False, default=uuid.uuid4)
    thread_id = Column(Integer, nullable=False)
    created = Column(DateTime, default=datetime.utcnow)
    updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    context_data = Column(JSON, nullable=True)  # JSON-Feld für zusätzliche Kontextdaten

    def to_dict(self):
        return {
            "id": self.id,
            "user": str(self.user),  # Convert UUID to string
            "thread_id": self.thread_id,
            "prompt_id": str(self.prompt_id),  # Convert UUID to string
            "created": self.created.isoformat(),  # Format datetime as ISO string
            "updated": self.updated.isoformat(),  # Format datetime as ISO string
            "context_data": self.context_data,  # Leave JSON as-is
        }

    class Config:
        orm_mode = True
        from_attributes = True