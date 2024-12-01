"""create api_keys table

Revision ID: 6bbad1d03808
Revises: 5aaad1d03808  # Replace with actual previous revision ID or set to None if first migration
Create Date: 2024-09-14 08:34:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '6bbad1d03808'
down_revision = '5aaad1d03808'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create the uuid-ossp extension if it doesn't exist
    op.execute('CREATE EXTENSION IF NOT EXISTS "uuid-ossp";')

    # Create the api_keys table
    op.create_table(
        'api_keys',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text("uuid_generate_v4()"), primary_key=True),
        sa.Column('user', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('key', sa.String(64), nullable=False),  # API key length is 64 characters
        sa.Column('created', sa.TIMESTAMP(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.ForeignKeyConstraint(['user'], ['users.uuid'], ondelete='CASCADE')  # Foreign key to users table
    )

    # Add an index to the key column for faster lookups
    op.create_index('ix_api_keys_key', 'api_keys', ['key'])


def downgrade() -> None:
    # Drop the table and its index
    op.drop_index('ix_api_keys_key', table_name='api_keys')
    op.drop_table('api_keys')
