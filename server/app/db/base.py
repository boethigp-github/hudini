

from ..config.settings import Settings

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base

settings = Settings()


Base = declarative_base()


SQLALCHEMY_DATABASE_URL = settings.get("default").get("DATABASE_URL")

engine = create_async_engine(SQLALCHEMY_DATABASE_URL, echo=True)
async_session_maker = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

