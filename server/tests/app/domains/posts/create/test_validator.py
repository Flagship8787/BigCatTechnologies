import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.posts.create.validator import Validator
from tests.app.domains.common.shared_specs import ValidatorBlankFieldSpec
from tests.conftest import create_blog


class TestValidator(ValidatorBlankFieldSpec):
    validator_class = Validator
    valid_kwargs = {"blog_id": "placeholder", "title": "My Title", "body": "Some body"}

    # Override: valid_kwargs uses a placeholder blog_id that won't exist in DB
    # Use db_session-aware test instead
    @pytest.mark.asyncio
    async def test_valid_with_all_fields(self, db_session: AsyncSession):
        blog = await create_blog(db_session)
        v = Validator(blog_id=blog.id, title="My Title", body="Some body")
        assert await v.validate(db_session) is True
        assert v.errors == {}

    @pytest.mark.asyncio
    async def test_invalid_without_blog_id(self, db_session: AsyncSession):
        v = Validator(blog_id="", title="My Title", body="Some body")
        assert await v.validate(db_session) is False
        assert "blog_id" in v.errors

    @pytest.mark.asyncio
    async def test_invalid_with_nonexistent_blog_id(self, db_session: AsyncSession):
        v = Validator(blog_id="nonexistent-id", title="My Title", body="Some body")
        assert await v.validate(db_session) is False
        assert "blog_id" in v.errors

    @pytest.mark.asyncio
    async def test_invalid_without_title(self, db_session: AsyncSession):
        blog = await create_blog(db_session)
        v = Validator(blog_id=blog.id, title="", body="Some body")
        assert await v.validate(db_session) is False
        assert "title" in v.errors

    @pytest.mark.asyncio
    async def test_invalid_without_body(self, db_session: AsyncSession):
        blog = await create_blog(db_session)
        v = Validator(blog_id=blog.id, title="My Title", body="")
        assert await v.validate(db_session) is False
        assert "body" in v.errors

    @pytest.mark.asyncio
    async def test_invalid_with_blank_whitespace_title(self, db_session: AsyncSession):
        blog = await create_blog(db_session)
        v = Validator(blog_id=blog.id, title="   ", body="Some body")
        assert await v.validate(db_session) is False
        assert "title" in v.errors

    @pytest.mark.asyncio
    async def test_collects_multiple_errors(self, db_session: AsyncSession):
        blog = await create_blog(db_session)
        v = Validator(blog_id=blog.id, title="", body="")
        assert await v.validate(db_session) is False
        assert "title" in v.errors
        assert "body" in v.errors
