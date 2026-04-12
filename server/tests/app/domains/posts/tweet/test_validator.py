import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.posts.tweet.validator import Validator
from app.models.post import PostState
from tests.conftest import create_post


class TestValidator:
    @pytest.mark.asyncio
    async def test_valid_starts_true(self, db_session: AsyncSession):
        post = await create_post(db_session, state=PostState.published.value)
        v = Validator(post=post)
        assert v.valid is True

    @pytest.mark.asyncio
    async def test_errors_start_empty(self, db_session: AsyncSession):
        post = await create_post(db_session, state=PostState.published.value)
        v = Validator(post=post)
        assert v.errors == {}

    @pytest.mark.asyncio
    async def test_valid_with_published_post(self, db_session: AsyncSession):
        post = await create_post(db_session, state=PostState.published.value)
        v = Validator(post=post)
        assert await v.validate(db_session) is True
        assert v.errors == {}

    @pytest.mark.asyncio
    async def test_invalid_when_post_is_none(self, db_session: AsyncSession):
        v = Validator(post=None)
        assert await v.validate(db_session) is False
        assert "post" in v.errors

    @pytest.mark.asyncio
    async def test_invalid_when_post_is_drafted(self, db_session: AsyncSession):
        post = await create_post(db_session, state=PostState.drafted.value)
        v = Validator(post=post)
        assert await v.validate(db_session) is False
        assert "state" in v.errors

    @pytest.mark.asyncio
    async def test_invalid_when_post_is_deleted(self, db_session: AsyncSession):
        post = await create_post(db_session, state=PostState.deleted.value)
        v = Validator(post=post)
        assert await v.validate(db_session) is False
        assert "state" in v.errors

    @pytest.mark.asyncio
    async def test_error_message_mentions_published(self, db_session: AsyncSession):
        post = await create_post(db_session, state=PostState.drafted.value)
        v = Validator(post=post)
        await v.validate(db_session)
        assert any("published" in msg for msg in v.errors["state"])
