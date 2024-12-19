"""Add model_parameter table

Revision ID: d49503a73659
Revises: 341fa5b68027
Create Date: 2024-12-10 07:09:13.184571

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'd49503a73659'
down_revision: Union[str, None] = '341fa5b68027'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create the 'model_parameter' table
    op.create_table(
        'model_parameter',
        sa.Column('uuid', postgresql.UUID(as_uuid=True), server_default=sa.text("uuid_generate_v4()"), primary_key=True),
        sa.Column('user', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.uuid', ondelete='CASCADE'), nullable=False),
        sa.Column('parameter', sa.String(length=200), nullable=True),
        sa.Column('model', sa.String(length=200), nullable=True),
        sa.Column('value', postgresql.JSON(), nullable=True),
        sa.Column('active', sa.Boolean(), server_default=sa.text('FALSE'), nullable=False),
        sa.Column('created', sa.TIMESTAMP(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('updated', sa.TIMESTAMP(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
    )

    # Add indexes
    op.create_index('ix_model_parameter_parameter', 'model_parameter', ['parameter'])
    op.create_index('ix_model_parameter_active', 'model_parameter', ['active'])


def downgrade() -> None:
    # Drop indexes
    op.drop_index('ix_model_parameter_parameter', table_name='model_parameter')
    op.drop_index('ix_model_parameter_active', table_name='model_parameter')

    # Drop the 'model_parameter' table
    op.drop_table('model_parameter')
