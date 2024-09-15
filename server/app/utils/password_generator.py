import bcrypt
import logging
logger = logging.getLogger(__name__)

def generate_password(password: str):
    return  bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')