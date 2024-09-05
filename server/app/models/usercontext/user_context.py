import json
from sqlalchemy import Column, BigInteger, DateTime, Text, ForeignKey
from datetime import datetime
from server.app.db.base import Base

class UserContextModel(Base):
    __tablename__ = 'user_context'

    id = Column(BigInteger, primary_key=True)
    context_data = Column(Text, nullable=False)
    user = Column(BigInteger, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    thread_id = Column(BigInteger, nullable=False)
    created = Column(DateTime, default=datetime.utcnow)
    updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def set_context_data(self, data):
        self.context_data = json.dumps(data)

    def get_context_data(self):
        return json.loads(self.context_data)

    def to_dict(self):
        return {
            "id": self.id,
            "user": self.user,
            "thread_id": self.thread_id,
            "created": self.created,
            "updated": self.updated,
            "context_data": self.get_context_data(),
        }