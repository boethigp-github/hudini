from fastapi import HTTPException, Request
import logging
logger = logging.getLogger(__name__)

async def check_user_session(request: Request):
    access_token = request.session.get('access_token')
    if not access_token:
        logger.debug("No access_token found in session")
        raise HTTPException(status_code=401, detail="No active session found")
    return access_token