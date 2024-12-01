import asyncio
import sqlalchemy as sa
from server.app.models.users.user import User
from server.app.db.get_db import get_db
from sqlalchemy.orm import selectinload
import unittest

class TestAbstract(unittest.TestCase):
    @classmethod
    async def async_init(cls):
        """Async initialization for database connections and API key retrieval."""
        # Retrieve the API key for the default admin user
        cls.api_key = await cls.get_api_key_for_admin()


    @classmethod
    async def get_api_key_for_admin(cls):
        """Retrieve the first API key for the default admin user."""
        async for session in get_db():
            # Fetch the admin user based on the username and eagerly load the api_keys relationship
            result = await session.execute(
                sa.select(User).options(selectinload(User.api_keys)).filter_by(username=cls.APP_DEFAULT_ADMIN_USERNAME)
            )
            admin_user = result.scalar()

            return admin_user.api_keys[0].key
