from typing import Optional
from fastapi import Request, Depends
from fastapi.security import APIKeyHeader
from sqlalchemy.ext.asyncio import AsyncSession
from server.app.utils.get_api_user import get_api_user
from server.app.utils.get_user_by_session import get_user_by_session
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
        return await get_api_user(api_key, db)
    else:
        logger.debug(f"api_key_or_session_auth Check userSession")
        return await get_user_by_session(request)
