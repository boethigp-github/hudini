from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import joinedload
from fastapi import Depends, HTTPException, Security, status
from fastapi.security import APIKeyHeader
from server.app.models.api_key.api_key import ApiKey
from server.app.db.get_db import get_db

# Security header for API key
api_key_header = APIKeyHeader(name="X-API-Key")

# Function to validate API key and fetch the corresponding user
async def get_api_user(api_key: str = Depends(api_key_header), db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(ApiKey)
        .options(joinedload(ApiKey.user_relationship))  # Use user_relationship since user is a relationship
        .filter(ApiKey.key == api_key, ApiKey.active == True)
    )
    api_key_entry = result.scalars().first()

    if not api_key_entry:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or inactive API Key",
            headers={"WWW-Authenticate": "API-Key"},
        )

    # Return the associated user
    return {"username": api_key_entry.user_relationship.username, "api_key": api_key_entry.key}
