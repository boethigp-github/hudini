"""Add active column to api_keys

Revision ID: 8dcad3e04810
Revises: 7ccad2d03809
Create Date: 2024-09-14 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '8dcad3e04810'
down_revision = '7ccad2d03809'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add 'active' column to 'api_keys' table, default is 0 (false)
    op.add_column('api_keys', sa.Column('active', sa.Boolean(), server_default=sa.text('FALSE'), nullable=False))


def downgrade() -> None:
    # Remove 'active' column from 'api_keys' table
    op.drop_column('api_keys', 'active')
