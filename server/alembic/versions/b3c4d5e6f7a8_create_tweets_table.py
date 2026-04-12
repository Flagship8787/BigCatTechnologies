"""create tweets table

Revision ID: b3c4d5e6f7a8
Revises: a1b2c3d4e5f6
Create Date: 2026-04-12 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b3c4d5e6f7a8'
down_revision: Union[str, None] = 'a1b2c3d4e5f6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'tweets',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('post_id', sa.String(36), sa.ForeignKey('posts.id'), nullable=False),
        sa.Column('tweet_id', sa.String(255), nullable=False),
        sa.Column('url', sa.String(500), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    )

    op.create_index('ix_tweets_post_id', 'tweets', ['post_id'])


def downgrade() -> None:
    op.drop_index('ix_tweets_post_id', table_name='tweets')
    op.drop_table('tweets')
