from sqlalchemy import Column, String, DateTime, BigInteger
from datetime import datetime
from server.app.db.base import Base  # Import Base from the shared module

# SQLAlchemy model
class User(Base):  # Use the Base directly
    __tablename__ = 'users'

    id = Column(BigInteger, primary_key=True, autoincrement=True)  # Primary key and auto-increment
    username = Column(String(50), nullable=False)
    email = Column(String(100), nullable=False, unique=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime, nullable=True)

    def to_dict(self):
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "created_at": self.created_at.isoformat(),  # Convert datetime to ISO format string
            "last_login": self.last_login.isoformat() if self.last_login else None  # Handle None case
        }
