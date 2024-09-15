"""create user as uuid in gripsbox

Revision ID: 14bf0e0cba51
Revises: be70a9a8025f
Create Date: 2024-09-15 19:39:08.216163

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '14bf0e0cba51'
down_revision: Union[str, None] = 'be70a9a8025f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add the user_uuid column to the gripsbox table
    op.add_column('gripsbox', sa.Column('user', sa.UUID(), nullable=False))

    # Add the foreign key constraint for user_uuid to reference users.uuid
    op.create_foreign_key(
        'fk_user',        # Constraint name
        'gripsbox',       # Table we're adding the foreign key to
        'users',          # Table we're referencing
        ['user'],    # Column(s) in the gripsbox table
        ['uuid'],         # Column(s) in the users table
        ondelete='CASCADE'  # Specify cascade behavior on delete
    )


def downgrade() -> None:
    # Remove the foreign key constraint
    op.drop_constraint('fk_user', 'gripsbox', type_='foreignkey')

    # Drop the user_uuid column from the gripsbox table
    op.drop_column('gripsbox', 'user_uuid')
