from sqlalchemy import Column, String, DateTime, BigInteger
from datetime import datetime
from server.app.db.base import Base  # Import Base from the shared module
from sqlalchemy.dialects.postgresql import UUID
import uuid
# SQLAlchemy model
class User(Base):  # Use the Base directly
    __tablename__ = 'users'

    uuid = Column(UUID(as_uuid=True), nullable=False, default=uuid.uuid4, primary_key=True)
    username = Column(String(50), nullable=False)
    email = Column(String(100), nullable=False, unique=True)
    created = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime, nullable=True)

    def to_dict(self):
        return {
            "id": str(self.uuid),
            "username": self.username,
            "email": self.email,
            "created": self.created.isoformat(),  # Convert datetime to ISO format string
            "last_login": self.last_login.isoformat() if self.last_login else None  # Handle None case
        }
