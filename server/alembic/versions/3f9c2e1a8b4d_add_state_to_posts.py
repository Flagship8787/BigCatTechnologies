"""add state to posts

Revision ID: 3f9c2e1a8b4d
Revises: 0be5f7a0dab5
Create Date: 2026-03-31 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "3f9c2e1a8b4d"
down_revision: Union[str, None] = "0be5f7a0dab5"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("posts", sa.Column("state", sa.String(50), nullable=False, server_default="drafted"))


def downgrade() -> None:
    op.drop_column("posts", "state")
