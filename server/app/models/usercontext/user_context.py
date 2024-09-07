from sqlalchemy import Column, BigInteger, DateTime, ForeignKey
from datetime import datetime
from sqlalchemy.dialects.postgresql import UUID as SQLUUID
from server.app.db.base import Base
from sqlalchemy.dialects.postgresql import JSONB
from fastapi.encoders import jsonable_encoder
import pytz
from server.app.config.settings import Settings
settings = Settings()

app_timezone = pytz.timezone(settings.get("default").get("APP_TIMEZONE"))

class UserContextModel(Base):
    __tablename__ = 'user_context'

    # Remove as_uuid=True and handle UUID as a regular type
    uuid = Column(SQLUUID, primary_key=True, nullable=False)
    context_data = Column(JSONB, nullable=False)
    user = Column(SQLUUID, ForeignKey('users.uuid', ondelete='CASCADE'), nullable=False)
    thread_id = Column(BigInteger, nullable=False)
    created = Column(DateTime, default=datetime.now(tz=app_timezone), nullable=False)
    updated = Column(DateTime, default=datetime.now(tz=app_timezone),onupdate=lambda: datetime.now(tz=app_timezone))

    def set_context_data(self, data):
        """ Serialize context_data with jsonable_encoder to handle UUID and complex types """
        self.context_data = jsonable_encoder(data)

    def get_context_data(self):
        """ Fetch the context_data without modification """
        return self.context_data

    def to_dict(self):
        context_data = self.get_context_data()
        return {
            "uuid": str(self.uuid),
            "user": str(self.user),
            "thread_id": self.thread_id,
            "created": self.created,
            "updated": self.updated,
            "prompt": context_data.get('prompt'),  # This should now include context_data within prompt
        }
