import logging
from fastapi import APIRouter, Request, HTTPException, Depends
from authlib.integrations.starlette_client import OAuth
from authlib.oauth2.rfc6749.errors import OAuth2Error
from starlette.responses import RedirectResponse
from pydantic import BaseModel
from typing import Dict, Any
from datetime import datetime
from server.app.config.settings import Settings
from server.app.services.user_service import UserService

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

router = APIRouter()
oauth = OAuth()
settings = Settings()

def setup_oauth():
    google_client_id = settings.get("default").get("APP_GOOGLE_AUTH_CLIENT_ID")
    google_client_secret = settings.get("default").get("APP_GOOGLE_AUTH_CLIENT_SECRET")
    google_redirect_uri = settings.get("default").get("APP_GOOGLE_AUTH_REDIRECT_URI")

    if not all([google_client_id, google_client_secret, google_redirect_uri]):
        logger.error("Missing Google OAuth configuration settings")
        raise ValueError("Missing Google OAuth configuration settings")

    oauth.register(
        name='google',
        client_id=google_client_id,
        client_secret=google_client_secret,
        authorize_url='https://accounts.google.com/o/oauth2/auth',
        access_token_url='https://accounts.google.com/o/oauth2/token',
        redirect_uri=google_redirect_uri,
        client_kwargs={'scope': 'openid email profile'},
        jwks_uri="https://www.googleapis.com/oauth2/v3/certs"
    )
    logger.debug("OAuth setup completed")

# Call setup_oauth at the module level
setup_oauth()

class SessionInfoResponseModel(BaseModel):
    access_token: Dict[str, Any]
    user_info: Dict[str, Any]

@router.get('/auth/login/google', tags=["authentication"])
async def login_google(request: Request):
    redirect_uri = settings.get("default").get("APP_GOOGLE_AUTH_REDIRECT_URI")
    logger.debug(f"Redirecting to Google for authentication, redirect URI: {redirect_uri}")
    return await oauth.google.authorize_redirect(request, redirect_uri)

from fastapi import Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from server.app.models.users.user import User
from server.app.db.get_db import get_db as get_async_session
import uuid

@router.get("/auth/session-info", tags=["authentication"], response_model=SessionInfoResponseModel)
async def get_session_info(
    request: Request,
    db: AsyncSession = Depends(get_async_session)
):
    access_token = request.session.get('access_token')
    user_info = request.session.get('user_info')

    if not access_token or not user_info:
        raise HTTPException(status_code=401, detail="No active session found")

    # Ensure both access_token and user_info are dictionaries
    if not isinstance(access_token, dict):
        access_token = {"token": str(access_token)}

    if not isinstance(user_info, dict):
        user_info = {
            "uuid": str(getattr(user_info, 'uuid', '')),
            "username": str(getattr(user_info, 'username', '')),
            "email": str(getattr(user_info, 'email', '')),
            "created": str(getattr(user_info, 'created', '')),
            "updated": str(getattr(user_info, 'updated', '')),
            "last_login": str(getattr(user_info, 'last_login', ''))
        }

    # Check database for session user
    user_uuid = user_info.get('uuid')
    if user_uuid:
        try:
            user_uuid_obj = uuid.UUID(user_uuid)
            result = await db.execute(select(User).filter(User.uuid == user_uuid_obj))
            user = result.scalar_one_or_none()
            if not user:
                # User is not available in the database
                raise HTTPException(status_code=401, detail="User no longer exists")
        except ValueError:
            # Invalid UUID
            raise HTTPException(status_code=401, detail="Invalid user identifier")

    return SessionInfoResponseModel(
        access_token=access_token,
        user_info=user_info
    )

@router.get('/auth/google/callback', tags=["authentication"])
async def auth_google_callback(request: Request, db: AsyncSession = Depends(get_async_session)):
    try:
        code = request.query_params.get("code")
        if not code:
            raise HTTPException(status_code=400, detail="Authorization code not found")

        token = await oauth.google.authorize_access_token(request)
        google_user_info = token['userinfo']
        email = google_user_info['email']

        # Try to load user by email
        result = await db.execute(select(User).filter(User.email == email))
        user = result.scalar_one_or_none()

        if not user:
            # User doesn't exist, create a new one using UserService
            user_service = UserService()
            user = await user_service.create_user(
                email=email,
                username=google_user_info.get('name', email.split('@')[0])
            )

        # Update last_login
        if hasattr(user, 'last_login'):
            user.last_login = datetime.utcnow()
        await db.commit()

        # Prepare user info for session
        user_dict = {}
        for attr in ['uuid', 'username', 'email', 'created', 'updated', 'last_login']:
            if hasattr(user, attr):
                value = getattr(user, attr)
                user_dict[attr] = str(value) if value is not None else None

        # Store token and user info in session
        request.session['access_token'] = dict(token)  # Ensure token is stored as a dictionary
        request.session['user_info'] = user_dict  # Store user info as a dictionary

        client_url = settings.get("default").get("CLIENT_URL")
        return RedirectResponse(url=client_url)

    except OAuth2Error as e:
        logger.error(f"Failed to handle Google OAuth callback: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Failed to handle Google OAuth callback: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

    except OAuth2Error as e:
        logger.error(f"Failed to handle Google OAuth callback: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Failed to handle Google OAuth callback: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

@router.get('/auth/logout', tags=["authentication"])
async def logout(request: Request):
    """
    Logs the user out by clearing the session.
    """
    try:
        # Clear the session data
        request.session.clear()

        # Return success response
        logger.debug("User successfully logged out.")
        return {"success": True}

    except Exception as e:
        logger.error(f"Error during logout: {str(e)}")
        raise HTTPException(status_code=500, detail="Logout failed due to server error")