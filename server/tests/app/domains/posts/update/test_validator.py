import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.posts.update.validator import Validator
from app.models.post import PostState
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
    async def test_valid_with_no_fields(self, db_session: AsyncSession):
        post = await create_post(db_session)
        v = Validator(post=post)
        assert await v.validate(db_session) is True
        assert v.errors == {}

    @pytest.mark.asyncio
    async def test_valid_with_all_fields(self, db_session: AsyncSession):
        post = await create_post(db_session)
        v = Validator(post=post, title="New Title", body="New body", state=PostState.published.value)
        assert await v.validate(db_session) is True
        assert v.errors == {}

    @pytest.mark.asyncio
    async def test_invalid_when_post_is_none(self, db_session: AsyncSession):
        v = Validator(post=None)
        assert await v.validate(db_session) is False
        assert "post" in v.errors

    @pytest.mark.asyncio
    async def test_invalid_with_blank_title(self, db_session: AsyncSession):
        post = await create_post(db_session)
        v = Validator(post=post, title="   ")
        assert await v.validate(db_session) is False
        assert "title" in v.errors

    @pytest.mark.asyncio
    async def test_invalid_with_empty_title(self, db_session: AsyncSession):
        post = await create_post(db_session)
        v = Validator(post=post, title="")
        assert await v.validate(db_session) is False
        assert "title" in v.errors

    @pytest.mark.asyncio
    async def test_invalid_with_blank_body(self, db_session: AsyncSession):
        post = await create_post(db_session)
        v = Validator(post=post, body="   ")
        assert await v.validate(db_session) is False
        assert "body" in v.errors

    @pytest.mark.asyncio
    async def test_invalid_with_unrecognized_state(self, db_session: AsyncSession):
        post = await create_post(db_session)
        v = Validator(post=post, state="banana")
        assert await v.validate(db_session) is False
        assert "state" in v.errors

    @pytest.mark.asyncio
    async def test_collects_multiple_errors(self, db_session: AsyncSession):
        post = await create_post(db_session)
        v = Validator(post=post, title="", body="   ")
        assert await v.validate(db_session) is False
        assert "title" in v.errors
        assert "body" in v.errors

    @pytest.mark.asyncio
    async def test_none_fields_are_not_validated(self, db_session: AsyncSession):
        post = await create_post(db_session)
        v = Validator(post=post, title=None, body=None, state=None)
        assert await v.validate(db_session) is True
