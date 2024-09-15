from sqlalchemy.ext.asyncio import AsyncSession
from server.app.db.base import async_session_maker

# Dependency to get the database session
async def get_db():
    async with async_session_maker() as session:
        yield session
