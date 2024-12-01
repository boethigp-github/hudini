from sqlalchemy import DateTime, Column, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from server.app.db.base import Base
import uuid
from datetime import datetime
from server.app.models.api_key.api_key import ApiKey
class User(Base):
    __tablename__ = 'users'

    uuid = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    created = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    updated = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = Column(DateTime(timezone=True), nullable=True)
    password = Column(String(128), nullable=False)

    # Relationship to ApiKey
    api_keys = relationship(ApiKey.get_class_name(), back_populates="user_relationship", cascade="all, delete", lazy="selectin")

    @staticmethod
    def get_class_name():
        return "User"

    def to_dict(self):
        return {
            "id": str(self.uuid),
            "username": self.username,
            "email": self.email,
            "created": self.created.isoformat(),
            "updated": self.updated.isoformat(),
            "last_login": self.last_login.isoformat() if self.last_login else None
        }

    def get_password_hash(self):
        return self.password