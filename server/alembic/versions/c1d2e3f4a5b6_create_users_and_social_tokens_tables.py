"""create users and social_tokens tables

Revision ID: c1d2e3f4a5b6
Revises: b3c4d5e6f7a8
Create Date: 2026-04-24 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c1d2e3f4a5b6'
down_revision: Union[str, None] = 'b3c4d5e6f7a8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'users',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('auth0_id', sa.String(255), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    )

    op.create_index('ix_users_auth0_id', 'users', ['auth0_id'], unique=True)

    op.create_table(
        'social_tokens',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('user_id', sa.String(36), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('provider', sa.String(50), nullable=False),
        sa.Column('access_token', sa.Text, nullable=False),
        sa.Column('refresh_token', sa.Text, nullable=True),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('provider_user_id', sa.String(255), nullable=True),
        sa.UniqueConstraint('user_id', 'provider', name='uq_social_tokens_user_provider'),
    )

    op.create_index('ix_social_tokens_user_id', 'social_tokens', ['user_id'])


def downgrade() -> None:
    op.drop_index('ix_social_tokens_user_id', table_name='social_tokens')
    op.drop_table('social_tokens')
    op.drop_index('ix_users_auth0_id', table_name='users')
    op.drop_table('users')
