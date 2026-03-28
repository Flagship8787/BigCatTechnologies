"""create blogs and posts tables

Revision ID: 0be5f7a0dab5
Revises:
Create Date: 2026-03-28 11:54:35.231219

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0be5f7a0dab5'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'blogs',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('description', sa.Text, nullable=False, server_default=''),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
    )

    op.create_table(
        'posts',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('blog_id', sa.String(36), sa.ForeignKey('blogs.id'), nullable=False),
        sa.Column('title', sa.String(500), nullable=False),
        sa.Column('body', sa.Text, nullable=False, server_default=''),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
    )

    op.create_index('ix_posts_blog_id', 'posts', ['blog_id'])


def downgrade() -> None:
    op.drop_index('ix_posts_blog_id', table_name='posts')
    op.drop_table('posts')
    op.drop_table('blogs')
