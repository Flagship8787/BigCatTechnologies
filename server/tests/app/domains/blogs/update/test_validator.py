import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.blogs.update.validator import Validator
from tests.app.domains.common.shared_specs import ValidatorBlankFieldSpec
from tests.conftest import create_blog


class TestValidator(ValidatorBlankFieldSpec):
    validator_class = Validator
    valid_kwargs = {"blog_id": "placeholder", "name": "New Name", "author_name": "Author"}

    @pytest.mark.asyncio
    async def test_valid_with_all_fields(self, db_session: AsyncSession):
        blog = await create_blog(db_session)
        v = Validator(blog_id=blog.id, name="New Name", author_name="New Author")
        assert await v.validate(db_session) is True
        assert v.errors == {}

    @pytest.mark.asyncio
    async def test_invalid_without_blog_id(self, db_session: AsyncSession):
        v = Validator(blog_id="", name="New Name", author_name="Author")
        assert await v.validate(db_session) is False
        assert "blog_id" in v.errors

    @pytest.mark.asyncio
    async def test_invalid_with_nonexistent_blog_id(self, db_session: AsyncSession):
        v = Validator(blog_id="nonexistent-id", name="New Name", author_name="Author")
        assert await v.validate(db_session) is False
        assert "blog_id" in v.errors

    @pytest.mark.asyncio
    async def test_invalid_without_name(self, db_session: AsyncSession):
        blog = await create_blog(db_session)
        v = Validator(blog_id=blog.id, name="", author_name="Author")
        assert await v.validate(db_session) is False
        assert "name" in v.errors

    @pytest.mark.asyncio
    async def test_invalid_without_author_name(self, db_session: AsyncSession):
        blog = await create_blog(db_session)
        v = Validator(blog_id=blog.id, name="New Name", author_name="")
        assert await v.validate(db_session) is False
        assert "author_name" in v.errors

    @pytest.mark.asyncio
    async def test_description_is_optional(self, db_session: AsyncSession):
        blog = await create_blog(db_session)
        v = Validator(blog_id=blog.id, name="Name", author_name="Author")
        assert await v.validate(db_session) is True

    @pytest.mark.asyncio
    async def test_description_may_be_empty_string(self, db_session: AsyncSession):
        blog = await create_blog(db_session)
        v = Validator(blog_id=blog.id, name="Name", author_name="Author", description="")
        assert await v.validate(db_session) is True

    @pytest.mark.asyncio
    async def test_collects_multiple_errors(self, db_session: AsyncSession):
        v = Validator(blog_id="", name="", author_name="")
        assert await v.validate(db_session) is False
        assert "blog_id" in v.errors
        assert "name" in v.errors
        assert "author_name" in v.errors
