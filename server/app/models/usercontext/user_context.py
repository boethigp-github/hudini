from sqlalchemy import Column, Integer, String, DateTime, JSON
from datetime import datetime
from ...db.base import Base  # Import Base aus dem gemeinsamen Modul
from sqlalchemy.dialects.postgresql import UUID
import uuid
class UserContextModel(Base):
    __tablename__ = 'user_context'  # Tabellenname in der Datenbank

    id = Column(Integer, primary_key=True, autoincrement=True)
    user = Column(Integer, nullable=False)  # Changed to bigint (Integer in SQLAlchemy)
    thread_id = Column(Integer, nullable=False)
    created = Column(DateTime, default=datetime.utcnow)
    updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    context_data = Column(JSON, nullable=True)  # JSON-Feld für zusätzliche Kontextdaten

    def to_dict(self):
        return {
            "id": self.id,
            "user": self.user,
            "thread_id": self.thread_id,
            "created": self.created.isoformat(),
            "updated": self.updated.isoformat(),
            "context_data": self.context_data,
        }

    # Removed the Config class as it is not necessary for SQLAlchemy models
