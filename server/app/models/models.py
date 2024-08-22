from server.app.extensions import db
from sqlalchemy.dialects.postgresql import UUID
import uuid
from datetime import datetime

class Prompt(db.Model):
    __tablename__ = 'prompts'

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    prompt = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    user = db.Column(db.String(30), nullable=False)
    status = db.Column(db.String(30), nullable=False)

    def to_dict(self):
        return {
            "id": str(self.id),
            "prompt": self.prompt,
            "timestamp": self.timestamp.isoformat(),
            "user": self.user,
            "status": self.status
        }
