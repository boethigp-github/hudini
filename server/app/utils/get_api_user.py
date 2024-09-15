from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import joinedload
from fastapi import Depends, HTTPException, Security, status
from fastapi.security import APIKeyHeader
from server.app.models.api_key.api_key import ApiKey
from server.app.db.get_db import get_db
# Security header for API key
api_key_header = APIKeyHeader(name="X-API-Key")

# Funktion, um den API-Key aus der Datenbank zu prüfen
async def get_api_user(api_key: str = Depends(api_key_header), db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(ApiKey)
        .options(joinedload(ApiKey.user))
        .filter(ApiKey.key == api_key, ApiKey.active == True)
    )
    api_key_entry = result.scalars().first()

    # Falls der API-Key nicht gefunden wurde oder inaktiv ist
    if not api_key_entry:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or inactive API Key",
            headers={"WWW-Authenticate": "API-Key"},
        )

    # Rückgabe des Benutzers, der mit dem API-Key verknüpft ist
    return {"username": str(api_key_entry.user), "api_key": api_key_entry.key}
