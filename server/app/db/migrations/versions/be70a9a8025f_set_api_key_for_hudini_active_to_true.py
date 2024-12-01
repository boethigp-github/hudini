"""set api key for hudini active to true

Revision ID: be70a9a8025f
Revises: 88e0b768bdd7
Create Date: 2024-09-15 10:32:21.878183

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import table, column
from sqlalchemy import String, Boolean
from sqlalchemy.dialects.postgresql import UUID

# revision identifiers, used by Alembic.
revision: str = 'be70a9a8025f'
down_revision: Union[str, None] = '88e0b768bdd7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Reference to the users table
    users_table = table(
        'users',
        column('uuid', UUID(as_uuid=True)),
        column('username', String)
    )

    # Query to find the UUID of user 'hudini'
    conn = op.get_bind()
    result = conn.execute(
        sa.select(users_table.c.uuid).where(users_table.c.username == 'hudini')
    )
    user_uuid = result.scalar()

    if user_uuid:
        # Update the active column for the API key of the user 'hudini' to True
        api_keys_table = table(
            'api_keys',
            column('user', UUID(as_uuid=True)),
            column('active', Boolean)
        )

        op.execute(
            api_keys_table.update()
            .where(api_keys_table.c.user == user_uuid)
            .values(active=True)
        )
    else:
        raise ValueError("User 'hudini' not found.")


def downgrade() -> None:
    # Reference to the users table
    users_table = table(
        'users',
        column('uuid', UUID(as_uuid=True)),
        column('username', String)
    )

    # Query to find the UUID of user 'hudini'
    conn = op.get_bind()
    result = conn.execute(
        sa.select(users_table.c.uuid).where(users_table.c.username == 'hudini')
    )
    user_uuid = result.scalar()

    if user_uuid:
        # Revert the active column for the API key of the user 'hudini' to False
        api_keys_table = table(
            'api_keys',
            column('user', UUID(as_uuid=True)),
            column('active', Boolean)
        )

        op.execute(
            api_keys_table.update()
            .where(api_keys_table.c.user == user_uuid)
            .values(active=False)
        )