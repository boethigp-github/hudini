"""Add password column to users table

Revision ID: 75b1aecd837f
Revises: 8dcad3e04810
Create Date: 2024-09-15 09:43:27.695538

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '75b1aecd837f'
down_revision: Union[str, None] = '8dcad3e04810'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None



def upgrade() -> None:
    # Add 'password' column to 'users' table
    op.add_column('users', sa.Column('password', sa.String(length=128), nullable=False))


def downgrade() -> None:
    # Remove 'password' column from 'users' table
    op.drop_column('users', 'password')