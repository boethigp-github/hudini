from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# Revision identifiers, used by Alembic
revision = '341fa5b68027'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create the uuid-ossp extension
    op.execute('CREATE EXTENSION IF NOT EXISTS "uuid-ossp";')
    op.execute('CREATE EXTENSION IF NOT EXISTS "pgcrypto";')

    # Users table
    op.create_table(
        'users',
        sa.Column('uuid', postgresql.UUID(as_uuid=True), server_default=sa.text("uuid_generate_v4()"), primary_key=True),
        sa.Column('username', sa.String(length=50), nullable=False, unique=True),
        sa.Column('email', sa.String(length=100), nullable=False, unique=True),
        sa.Column('created', sa.TIMESTAMP(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('updated', sa.TIMESTAMP(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
        sa.Column('last_login', sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column('password', sa.String(length=128), nullable=False),
    )

    op.execute("""
    CREATE OR REPLACE FUNCTION create_api_key_for_user()
    RETURNS TRIGGER AS $$
    DECLARE
        new_api_key TEXT;
    BEGIN
        new_api_key := encode(gen_random_bytes(32), 'hex');
        INSERT INTO api_keys("user", key, created)
        VALUES (NEW.uuid, new_api_key, now());
        RETURN NEW;
    END;
    $$ LANGUAGE plpgsql;
    """)

    op.execute("""
    CREATE TRIGGER trigger_create_api_key
    AFTER INSERT ON users
    FOR EACH ROW EXECUTE FUNCTION create_api_key_for_user();
    """)

    # API Keys table
    op.create_table(
        'api_keys',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text("uuid_generate_v4()"), primary_key=True),
        sa.Column('user', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.uuid', ondelete='CASCADE'), nullable=False),
        sa.Column('key', sa.String(length=64), nullable=False),
        sa.Column('created', sa.TIMESTAMP(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('active', sa.Boolean(), server_default=sa.text('FALSE'), nullable=False),
    )
    op.create_index('ix_api_keys_key', 'api_keys', ['key'])

    # Gripsbox table
    op.create_table(
        'gripsbox',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text("uuid_generate_v4()"), primary_key=True),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('size', sa.Integer(), nullable=False),
        sa.Column('type', sa.String(), nullable=False),
        sa.Column('active', sa.Boolean(), nullable=False),
        sa.Column('created', sa.TIMESTAMP(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('updated', sa.TIMESTAMP(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('user', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.uuid', ondelete='CASCADE'), nullable=False),
        sa.Column('tags', sa.JSON(), nullable=False),
        sa.Column('models', sa.JSON(), nullable=True),
    )

    op.execute("""
    CREATE OR REPLACE FUNCTION update_modified_column()
    RETURNS TRIGGER AS $$
    BEGIN
        NEW.updated = now();
        RETURN NEW;
    END;
    $$ language 'plpgsql';
    """)

    op.execute("""
    CREATE TRIGGER update_gripsbox_modtime
    BEFORE UPDATE ON gripsbox
    FOR EACH ROW EXECUTE FUNCTION update_modified_column();
    """)

    # Prompts table
    op.create_table(
        'prompts',
        sa.Column('uuid', postgresql.UUID(as_uuid=True), server_default=sa.text("uuid_generate_v4()"), primary_key=True),
        sa.Column('prompt', sa.Text(), nullable=False),
        sa.Column('status', sa.String(length=50), nullable=False),
        sa.Column('user', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.uuid', ondelete='CASCADE'), nullable=False),
        sa.Column('created', sa.TIMESTAMP(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
    )

    # User Context table
    op.create_table(
        'user_context',
        sa.Column('uuid', postgresql.UUID(as_uuid=True), server_default=sa.text("uuid_generate_v4()"), primary_key=True),
        sa.Column('context_data', sa.JSONB(), nullable=False),
        sa.Column('user', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.uuid', ondelete='CASCADE'), nullable=False),
        sa.Column('thread_id', sa.BigInteger(), nullable=False),
        sa.Column('created', sa.TIMESTAMP(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('updated', sa.TIMESTAMP(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
    )


def downgrade() -> None:
    # Drop tables and triggers in reverse order
    op.drop_table('user_context')
    op.drop_table('prompts')

    op.execute("DROP TRIGGER IF EXISTS update_gripsbox_modtime ON gripsbox;")
    op.execute("DROP FUNCTION IF EXISTS update_modified_column;")
    op.drop_table('gripsbox')

    op.drop_index('ix_api_keys_key', table_name='api_keys')
    op.drop_table('api_keys')

    op.execute("DROP TRIGGER IF EXISTS trigger_create_api_key ON users;")
    op.execute("DROP FUNCTION IF EXISTS create_api_key_for_user;")
    op.drop_table('users')
