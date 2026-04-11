import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.posts.share_x.validator import Validator
from tests.conftest import create_post


class TestValidator:
    @pytest.mark.asyncio
    async def test_valid_starts_true(self, db_session: AsyncSession):
        post = await create_post(db_session)
        v = Validator(post=post)
        assert v.valid is True

    @pytest.mark.asyncio
    async def test_errors_start_empty(self, db_session: AsyncSession):
        post = await create_post(db_session)
        v = Validator(post=post)
        assert v.errors == {}

    @pytest.mark.asyncio
    async def test_valid_with_post(self, db_session: AsyncSession):
        post = await create_post(db_session)
        v = Validator(post=post)
        assert await v.validate(db_session) is True
        assert v.errors == {}

    @pytest.mark.asyncio
    async def test_invalid_when_post_is_none(self, db_session: AsyncSession):
        v = Validator(post=None)
        assert await v.validate(db_session) is False
        assert "post" in v.errors
