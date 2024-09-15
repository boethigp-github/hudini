from server.app.models.users.user import User
from server.app.utils.password_generator import generate_password
from sqlalchemy.ext.asyncio import AsyncSession
import random
import string
import logging

logger = logging.getLogger(__name__)


class UserService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_user(self, email: str, username: str = None):
        random_password = ''.join(random.choices(string.ascii_letters + string.digits, k=16))
        hashed_password = generate_password(random_password)

        new_user = User(
            username=username or email.split('@')[0],
            email=email,
            password=hashed_password
        )
        self.db.add(new_user)
        await self.db.commit()
        await self.db.refresh(new_user)

        logger.info(f"Created new user with email: {email}")
        return new_user

    # Add other user-related methods here as needed