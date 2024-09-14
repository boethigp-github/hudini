import logging
import requests
from fastapi import APIRouter, Request, HTTPException
from authlib.integrations.starlette_client import OAuth
from authlib.jose import jwt
from authlib.oauth2.rfc6749.errors import OAuth2Error
from server.app.config.settings import Settings
from pydantic import BaseModel
# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
import time
router = APIRouter()
oauth = OAuth()
settings = Settings()
from fastapi.responses import RedirectResponse
from fastapi import Response

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

def get_jwks():
    jwks_url = 'https://www.googleapis.com/oauth2/v3/certs'
    response = requests.get(jwks_url)
    response.raise_for_status()
    return response.json()


def validate_token(access_token):
    decoded_token = jwt.decode(access_token, algorithms=['RS256'], options={'verify_signature': False})
    expiration_timestamp = decoded_token['exp']
    current_timestamp = time.time()
    return expiration_timestamp > current_timestamp

@router.get('/auth/login/google', tags=["authentication"])
async def login_google(request: Request):
    redirect_uri = settings.get("default").get("APP_GOOGLE_AUTH_REDIRECT_URI")
    logger.debug(f"Redirecting to Google for authentication, redirect URI: {redirect_uri}")
    return await oauth.google.authorize_redirect(request, redirect_uri)


# Define the ResponseModel for session info
class SessionInfoResponseModel(BaseModel):
    access_token: str
    user_info: dict

@router.get("/auth/session-info", tags=["authentication"], response_model=SessionInfoResponseModel)
async def get_session_info(request: Request):
    access_token = request.session.get('access_token')
    user_info = request.session.get('user_info')

    if not access_token or not user_info:
        raise HTTPException(status_code=401, detail="No active session found")

    return SessionInfoResponseModel(
        access_token=access_token,
        user_info=user_info
    )

@router.get('/auth/google/callback', tags=["authentication"])
async def auth_google_callback(request: Request):
    try:
        code = request.query_params.get("code")
        logger.debug(f"Received code: {code}")
        if not code:
            logger.error("Authorization code not found in callback request")
            raise HTTPException(status_code=400, detail="Authorization code not found")
        token = await oauth.google.authorize_access_token(request)
        logger.debug(f"Received access token: {token}")
        user_info = token.get('userinfo')
        if not user_info:
            logger.error("User info not found in token")
            raise HTTPException(status_code=400, detail="User info not found in token")
        request.session['access_token'] = token['access_token']
        request.session['user_info'] = user_info
        client_url = settings.get("default").get("CLIENT_URL")
        redirect_url = f"{client_url}"
        return RedirectResponse(url=redirect_url)
    except OAuth2Error as e:
        logger.error(f"Failed to handle Google OAuth callback: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Failed to handle Google OAuth callback: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Unexpected error: {str(e)}")