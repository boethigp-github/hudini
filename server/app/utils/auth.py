from typing import Optional
from fastapi import Security, Request, HTTPException, Depends, status
from fastapi.security import APIKeyHeader
from sqlalchemy.ext.asyncio import AsyncSession
from server.app.utils.get_api_user import get_api_user
from server.app.utils.check_user_session import check_user_session
from server.app.db.get_db import get_db
import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Security header for API key
api_key_header = APIKeyHeader(name="X-API-Key")

async def auth(
    api_key: Optional[str] =None,
    request: Request = None,
    db: AsyncSession = Depends(get_db)
):

    if api_key:
        logger.debug(f"Received API key: {api_key[:4]}****")
        user = await get_api_user(api_key, db)
        return user
    else:
        logger.debug(f"api_key_or_session_auth Check userSession")
        access_token = await check_user_session(request)
        return {"username": "oauth_user", "token": access_token}
