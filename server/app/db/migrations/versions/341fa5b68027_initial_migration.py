from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '341fa5b68027'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create the uuid-ossp extension if it doesn't exist
    op.execute('CREATE EXTENSION IF NOT EXISTS "uuid-ossp";')

    # Creating the users table first with unique constraints on username and email
    op.create_table(
        'users',
        sa.Column('uuid', postgresql.UUID(as_uuid=True), server_default=sa.text("uuid_generate_v4()"),
                  primary_key=True),
        sa.Column('username', sa.VARCHAR(length=50), nullable=False, unique=True),  # Unique constraint on username
        sa.Column('email', sa.VARCHAR(length=100), nullable=False, unique=True),  # Unique constraint on email
        sa.Column('created', sa.TIMESTAMP(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('updated', sa.TIMESTAMP(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
        sa.Column('last_login', sa.TIMESTAMP(timezone=True), nullable=True),
    )

    # Creating the prompts table (dependent on users)
    op.create_table(
        'prompts',
        sa.Column('uuid', postgresql.UUID(as_uuid=True), server_default=sa.text("uuid_generate_v4()"),
                  primary_key=True,  nullable=False, unique=True),
        sa.Column('prompt', sa.TEXT(), nullable=False),
        sa.Column('status', sa.VARCHAR(length=50), nullable=False),
        sa.Column('user', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.uuid', ondelete='CASCADE'), nullable=False),
        sa.Column('created', sa.TIMESTAMP(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
    )

    # Creating the user_context table (dependent on users)
    op.create_table(
        'user_context',
        sa.Column('uuid', postgresql.UUID(as_uuid=True), server_default=sa.text("uuid_generate_v4()"),
                  primary_key=True),
        sa.Column('context_data', postgresql.JSONB(), nullable=False),
        sa.Column('user', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.uuid', ondelete='CASCADE'), nullable=False),
        sa.Column('thread_id', sa.BIGINT(), nullable=False),
        sa.Column('created', sa.TIMESTAMP(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('updated', sa.TIMESTAMP(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
    )

    # Insert the administrator user with the current timestamp
    op.execute(
        """
        INSERT INTO users (uuid, username, email, last_login)
        VALUES ('5baab051-0c32-42cf-903d-035ec6912a91', 'administrator', 'admin@hudini.eu', CURRENT_TIMESTAMP);
        """
    )


def table_exists(table_name):
    """Helper function to check if a table exists in the database."""
    conn = op.get_bind()
    result = conn.execute(
        sa.text(
            "SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name=:table_name)"
        ),
        {"table_name": table_name}
    )
    return result.scalar()


def downgrade() -> None:
    # Check if the tables exist before dropping them
    if table_exists('user_context'):
        op.drop_table('user_context')

    if table_exists('prompts'):
        op.drop_table('prompts')

    if table_exists('users'):
        op.drop_table('users')
