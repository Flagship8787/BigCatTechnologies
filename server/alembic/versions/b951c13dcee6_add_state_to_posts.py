"""add state to posts

Revision ID: b951c13dcee6
Revises: 0be5f7a0dab5
Create Date: 2026-03-31 09:51:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b951c13dcee6'
down_revision: Union[str, None] = '0be5f7a0dab5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        'posts',
        sa.Column('state', sa.String(50), nullable=False, server_default='drafted'),
    )


def downgrade() -> None:
    op.drop_column('posts', 'state')
