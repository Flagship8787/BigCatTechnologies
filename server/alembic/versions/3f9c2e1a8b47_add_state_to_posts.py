"""add state to posts

Revision ID: 3f9c2e1a8b47
Revises: 0be5f7a0dab5
Create Date: 2026-03-31 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "3f9c2e1a8b47"
down_revision = "0be5f7a0dab5"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("posts", sa.Column("state", sa.String(50), nullable=False, server_default="drafted"))


def downgrade() -> None:
    op.drop_column("posts", "state")
