from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# Revision identifiers, used by Alembic
revision = '341fa5b68027'
down_revision = None
branch_labels = None
depends_on = None


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


def upgrade() -> None:
    # Check and create the 'users' table
    if not table_exists('users'):
        op.create_table(
            'users',
            sa.Column('uuid', postgresql.UUID(as_uuid=True), server_default=sa.text("uuid_generate_v4()"),
                      primary_key=True),
            sa.Column('username', sa.String(length=50), nullable=False, unique=True),
            sa.Column('email', sa.String(length=100), nullable=False, unique=True),
            sa.Column('created', sa.TIMESTAMP(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'),
                      nullable=False),
            sa.Column('updated', sa.TIMESTAMP(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'),
                      nullable=True),
            sa.Column('last_login', sa.TIMESTAMP(timezone=True), nullable=True),
            sa.Column('password', sa.String(length=128), nullable=False),
        )

    # Check and create the 'api_keys' table
    if not table_exists('api_keys'):
        op.create_table(
            'api_keys',
            sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text("uuid_generate_v4()"),
                      primary_key=True),
            sa.Column('user', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.uuid', ondelete='CASCADE'),
                      nullable=False),
            sa.Column('key', sa.String(length=64), nullable=False),
            sa.Column('created', sa.TIMESTAMP(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'),
                      nullable=False),
            sa.Column('active', sa.Boolean(), server_default=sa.text('FALSE'), nullable=False),
        )
        op.create_index('ix_api_keys_key', 'api_keys', ['key'])

    # Check and create the 'gripsbox' table
    if not table_exists('gripsbox'):
        op.create_table(
            'gripsbox',
            sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text("uuid_generate_v4()"),
                      primary_key=True),
            sa.Column('name', sa.String(), nullable=False),
            sa.Column('size', sa.Integer(), nullable=False),
            sa.Column('type', sa.String(), nullable=False),
            sa.Column('active', sa.Boolean(), nullable=False),
            sa.Column('tags', sa.JSON(), nullable=False),
            sa.Column('models', sa.JSON(), nullable=True),
            sa.Column('created', sa.TIMESTAMP(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'),
                      nullable=False),
            sa.Column('updated', sa.TIMESTAMP(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'),
                      nullable=False),
            sa.ForeignKeyConstraint(['user'], ['users.uuid'], ondelete='CASCADE'),
        )

    # Add other tables similarly
    # Example for 'prompts' and 'user_context'

    if not table_exists('prompts'):
        op.create_table(
            'prompts',
            sa.Column('uuid', postgresql.UUID(as_uuid=True), server_default=sa.text("uuid_generate_v4()"),
                      primary_key=True),
            sa.Column('prompt', sa.Text(), nullable=False),
            sa.Column('status', sa.String(length=50), nullable=False),
            sa.Column('user', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.uuid', ondelete='CASCADE'),
                      nullable=False),
            sa.Column('created', sa.TIMESTAMP(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'),
                      nullable=False),
        )

    if not table_exists('user_context'):
        op.create_table(
            'user_context',
            sa.Column('uuid', postgresql.UUID(as_uuid=True), server_default=sa.text("uuid_generate_v4()"),
                      primary_key=True),
            sa.Column('context_data', postgresql.JSONB(), nullable=False),
            sa.Column('user', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.uuid', ondelete='CASCADE'),
                      nullable=False),
            sa.Column('thread_id', sa.BigInteger(), nullable=False),
            sa.Column('created', sa.TIMESTAMP(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'),
                      nullable=False),
            sa.Column('updated', sa.TIMESTAMP(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'),
                      nullable=True),
        )


def downgrade() -> None:
    # Drop tables in reverse order of creation
    op.drop_table('user_context')
    op.drop_table('prompts')
    op.drop_table('gripsbox')
    op.drop_index('ix_api_keys_key', table_name='api_keys')
    op.drop_table('api_keys')
    op.drop_table('users')
