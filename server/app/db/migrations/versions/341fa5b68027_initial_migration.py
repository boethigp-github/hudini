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
        sa.Column('id', sa.BIGINT(), primary_key=True),
        sa.Column('username', sa.VARCHAR(length=50), nullable=False, unique=True),  # Unique constraint on username
        sa.Column('email', sa.VARCHAR(length=100), nullable=False, unique=True),    # Unique constraint on email
        sa.Column('created_at', sa.TIMESTAMP(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
        sa.Column('last_login', sa.TIMESTAMP(), nullable=True),
    )

    # Creating the prompts table (dependent on users)
    op.create_table(
        'prompts',
        sa.Column('id', sa.BIGINT(), primary_key=True),
        sa.Column('prompt', sa.TEXT(), nullable=False),
        sa.Column('status', sa.VARCHAR(length=50), nullable=False),
        sa.Column('uuid', postgresql.UUID(as_uuid=True), server_default=sa.text("uuid_generate_v4()"), nullable=False, unique=True),
        sa.Column('user', sa.BIGINT(), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('created_at', sa.TIMESTAMP(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
    )

    # Creating the user_context table (dependent on users)
    op.create_table(
        'user_context',
        sa.Column('id', sa.BIGINT(), primary_key=True),
        sa.Column('context_data', sa.TEXT(), nullable=False),  # Changed from JSON to TEXT and made non-nullable
        sa.Column('user', sa.BIGINT(), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('thread_id', sa.BIGINT(), nullable=False),
        sa.Column('created', sa.TIMESTAMP(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),  # Changed to non-nullable
        sa.Column('updated', sa.TIMESTAMP(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),  # Changed to non-nullable
    )

    # Insert the administrator user
    op.execute(
        """
        INSERT INTO users (username, email, created_at, last_login)
        VALUES ('administrator', 'admin@hudini.eu', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP);
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