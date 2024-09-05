from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy import create_engine  # For synchronous migrations
from sqlalchemy.pool import NullPool
from server.app.config.settings import Settings

settings = Settings()

# Create the Base class for declarative models
Base = declarative_base()

# Configuration for async engine (for FastAPI)
SQLALCHEMY_DATABASE_URL_ASYNC = settings.get("default").get("DATABASE_URL")

# Async engine settings
engine_args = {
    "echo": settings.get("default").get("DB_SQL_ECHO", 'False') == 'True',
}

use_null_pool = settings.get("default").get("DB_USE_NULL_POOL", 'False') == 'True'

if use_null_pool:
    engine_args["poolclass"] = NullPool
else:
    engine_args.update({
        "pool_size": int(settings.get("default").get("DB_POOL_SIZE", 20)),
        "max_overflow": int(settings.get("default").get("DB_MAX_OVERFLOW", 5)),
        "pool_timeout": int(settings.get("default").get("DB_POOL_TIMEOUT", 30)),
        "pool_recycle": int(settings.get("default").get("DB_POOL_RECYCLE", 1800)),
    })

# Asynchronous engine (for FastAPI)
async_engine = create_async_engine(SQLALCHEMY_DATABASE_URL_ASYNC, **engine_args)

# Async session maker
async_session_maker = sessionmaker(
    async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False
)

# Synchronous engine (for Alembic migrations)
SQLALCHEMY_DATABASE_URL_SYNC = SQLALCHEMY_DATABASE_URL_ASYNC.replace("postgresql+asyncpg", "postgresql+psycopg2")
sync_engine = create_engine(SQLALCHEMY_DATABASE_URL_SYNC)

# Sync session maker for Alembic migrations
sync_session_maker = sessionmaker(bind=sync_engine)

# Async DB handling for FastAPI
async def get_db():
    async with async_session_maker() as session:
        try:
            yield session
        finally:
            await session.close()

async def init_db():
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def check_db_connection():
    try:
        async with async_engine.connect() as conn:
            await conn.execute("SELECT 1")
        return True
    except Exception as e:
        print(f"Fehler bei der Überprüfung der Datenbankverbindung: {e}")
        return False

async def close_db_connection():
    await async_engine.dispose()

__all__ = ["Base", "async_engine", "sync_engine", "async_session_maker", "sync_session_maker", "get_db", "init_db", "check_db_connection", "close_db_connection"]
