"""add models as json in gripsbox

Revision ID: 824082b59222
Revises: f99726437c00
Create Date: 2024-09-15 20:41:03.233157

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '824082b59222'
down_revision = 'f99726437c00'
branch_labels = None
depends_on = None

def upgrade() -> None:
    # Add the 'models' JSONB column to the 'gripsbox' table
    op.add_column('gripsbox', sa.Column('models', sa.JSON, nullable=True))

def downgrade() -> None:
    # Drop the 'models' column if we downgrade the migration
    op.drop_column('gripsbox', 'models')
