from server.app.utils.password_generator import generate_password
from sqlalchemy.future import select
from server.app.models.users.user import User
from server.app.db.get_db import get_db
import random
import string
import logging

logger = logging.getLogger(__name__)

class UserService:

    async def create_user(self, email: str, username: str = None):
        # Get a session from get_db
        async for db in get_db():
            random_password = ''.join(random.choices(string.ascii_letters + string.digits, k=16))
            hashed_password = generate_password(random_password)

            new_user = User(
                username=username or email.split('@')[0],
                email=email,
                password=hashed_password
            )
            db.add(new_user)
            await db.commit()
            await db.refresh(new_user)

            logger.info(f"Created new user with email: {email}")
            return new_user

    async def get_by_username(self, username: str) -> User:
        # Get a session from get_db
        async for db in get_db():
            result = await db.execute(select(User).filter(User.username == username))
            return result.scalar_one_or_none()

    async def get_all_users(self) -> list[dict]:
        """
        Retrieve all users from the database.

        Returns:
            list[dict]: A list of user dictionaries containing username and email.
        """
        async for db in get_db():
            result = await db.execute(select(User))
            users = result.scalars().all()
            return [{"username": user.username, "email": user.email} for user in users]