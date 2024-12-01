from fastapi import HTTPException, Request, Depends
from server.app.services.user_service import UserService
from sqlalchemy.ext.asyncio import AsyncSession

import logging

logger = logging.getLogger(__name__)

from fastapi import HTTPException, Request, Depends
from server.app.services.user_service import UserService

import logging

logger = logging.getLogger(__name__)

async def get_user_by_session(request: Request):
    access_token = request.session.get('access_token')
    user_info = request.session.get('user_info')

    if not access_token or not user_info:
        logger.debug("No access_token or user_info found in session")
        raise HTTPException(status_code=401, detail="No active session found")

    # Extract the username from the session
    username = user_info.get('username')

    user_service = UserService()
    user = await user_service.get_by_username(username)

    if not user:
        logger.debug(f"User with username {username} not found in the database")
        raise HTTPException(status_code=401, detail="User not found")

    # Return the user object
    return user

