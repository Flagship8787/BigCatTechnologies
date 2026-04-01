"""add_author_name_and_owner_id_to_blogs

Revision ID: a1b2c3d4e5f6
Revises: 3f9c2e1a8b4d
Create Date: 2026-04-01 16:47:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, None] = '3f9c2e1a8b4d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add author_name as nullable first so existing rows don't violate the constraint
    op.add_column('blogs', sa.Column('author_name', sa.String(255), nullable=True))
    op.execute("UPDATE blogs SET author_name = 'some-author' WHERE author_name IS NULL")
    op.alter_column('blogs', 'author_name', nullable=False)

    # Add owner_id (Auth0 sub claim) — seed existing rows with a placeholder
    op.add_column('blogs', sa.Column('owner_id', sa.String(255), nullable=True))
    op.execute("UPDATE blogs SET owner_id = 'unknown' WHERE owner_id IS NULL")
    op.alter_column('blogs', 'owner_id', nullable=False)


def downgrade() -> None:
    op.drop_column('blogs', 'owner_id')
    op.drop_column('blogs', 'author_name')
