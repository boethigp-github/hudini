"""create gripsbox table

Revision ID: 5aaad1d03808
Revises: abcd1234efgh  # Replace with actual previous revision ID or set to None if first migration
Create Date: 2024-09-13 08:34:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '5aaad1d03808'
down_revision = '341fa5b68027'  # Replace with actual previous revision ID or set to None if first migration
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create the uuid-ossp extension if it doesn't exist
    op.execute('CREATE EXTENSION IF NOT EXISTS "uuid-ossp";')

    # Create the gripsbox table
    op.create_table(
        'gripsbox',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text("uuid_generate_v4()"), primary_key=True),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('size', sa.Integer(), nullable=False),
        sa.Column('type', sa.String(), nullable=False),
        sa.Column('active', sa.Boolean(), nullable=False),
        sa.Column('tags', postgresql.ARRAY(sa.String()), nullable=False),
        sa.Column('created', sa.TIMESTAMP(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('updated', sa.TIMESTAMP(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
    )

    # Add a trigger to automatically update the 'updated' column
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
            FOR EACH ROW
        EXECUTE FUNCTION update_modified_column();
    """)


def downgrade() -> None:
    # Drop the table
    op.drop_table('gripsbox')

    # Remove the trigger function
    op.execute("DROP TRIGGER IF EXISTS update_gripsbox_modtime ON gripsbox;")
    op.execute("DROP FUNCTION IF EXISTS update_modified_column();")
