"""Insert initial user into users table

Revision ID: 9ecad3e04812
Revises: 9dcad3e04811
Create Date: 2024-09-15 13:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import table, column
from sqlalchemy import String
import sys, os
# Add the project root to sys.path so Python can find 'server'
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../../../')))

from server.app.utils.password_generator import generate_password
# revision identifiers, used by Alembic.
revision: str = '88e0b768bdd7'
down_revision: str= '75b1aecd837f'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create a temporary table structure for inserting the user
    users_table = table(
        'users',
        column('uuid', String),
        column('username', String),
        column('email', String),
        column('password', String),
    )

    # Hash the password using bcrypt
    hashed_password = generate_password("admin#123")

    # Insert the user into the table
    op.bulk_insert(users_table, [
        {
            'uuid': '5baab051-0c32-42cf-903d-035ec6912a91',
            'username': 'hudini',
            'email': 'brain@hudini.de',
            'password': hashed_password
        }
    ])


def downgrade() -> None:
    # Delete the inserted user during downgrade
    op.execute(
        "DELETE FROM users WHERE uuid = '5baab051-0c32-42cf-903d-035ec6912a91'"
    )
