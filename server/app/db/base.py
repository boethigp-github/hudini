from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.pool import NullPool
from ..config.settings import Settings

settings = Settings()

# Erstellen der Basis-Klasse für deklarative Modelle
Base = declarative_base()

# Konfiguration der Datenbankverbindung
SQLALCHEMY_DATABASE_URL = settings.get("default").get("DATABASE_URL")

# Engine-Konfiguration
engine_args = {
    "echo": settings.get("default").get("DB_SQL_ECHO", 'False') == 'True',  # Konvertierung zu Boolean
}

use_null_pool = settings.get("default").get("DB_USE_NULL_POOL", 'False') == 'True'  # Konvertierung zu Boolean

if use_null_pool:
    engine_args["poolclass"] = NullPool
else:
    engine_args.update({
        "pool_size": int(settings.get("default").get("DB_POOL_SIZE", 20)),
        "max_overflow": int(settings.get("default").get("DB_MAX_OVERFLOW", 5)),
        "pool_timeout": int(settings.get("default").get("DB_POOL_TIMEOUT", 30)),
        "pool_recycle": int(settings.get("default").get("DB_POOL_RECYCLE", 1800)),
    })

# Erstellen der Engine mit optimierten Einstellungen
engine = create_async_engine(SQLALCHEMY_DATABASE_URL, **engine_args)

# Erstellen des Session-Makers
async_session_maker = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False
)

async def get_db():
    async with async_session_maker() as session:
        try:
            yield session
        finally:
            await session.close()

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def check_db_connection():
    try:
        async with engine.connect() as conn:
            await conn.execute("SELECT 1")
        return True
    except Exception as e:
        print(f"Fehler bei der Überprüfung der Datenbankverbindung: {e}")
        return False

async def close_db_connection():
    await engine.dispose()

__all__ = ["Base", "engine", "async_session_maker", "get_db", "init_db", "check_db_connection", "close_db_connection"]