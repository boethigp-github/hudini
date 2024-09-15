"""change tags to json in gripsbox

Revision ID: f99726437c00
Revises: 14bf0e0cba51
Create Date: 2024-09-15 20:24:05.592511

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'f99726437c00'
down_revision = '14bf0e0cba51'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Drop the tags column and recreate it as JSON
    op.drop_column('gripsbox', 'tags')
    op.add_column('gripsbox', sa.Column('tags', sa.JSON(), nullable=False))


def downgrade() -> None:
    # Revert back to character varying[]
    op.drop_column('gripsbox', 'tags')
    op.add_column('gripsbox', sa.Column('tags', sa.ARRAY(sa.VARCHAR()), nullable=False))
