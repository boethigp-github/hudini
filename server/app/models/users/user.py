from sqlalchemy import DateTime
from datetime import datetime
import uuid
from sqlalchemy.orm import relationship
from sqlalchemy import Column, String
from sqlalchemy.dialects.postgresql import UUID
from server.app.db.base import Base
from server.app.models.api_key.api_key import ApiKey
class User(Base):
    __tablename__ = 'users'

    uuid = Column(UUID(as_uuid=True), nullable=False, default=uuid.uuid4, primary_key=True)
    username = Column(String(50), nullable=False)
    email = Column(String(100), nullable=False, unique=True)
    created = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime, nullable=True)

    # Relationship to ApiKey
    api_keys = relationship("ApiKey", back_populates="user_relationship", cascade="all, delete", lazy="selectin")

    def to_dict(self):
        return {
            "id": str(self.uuid),
            "username": self.username,
            "email": self.email,
            "created": self.created.isoformat(),
            "last_login": self.last_login.isoformat() if self.last_login else None
        }
