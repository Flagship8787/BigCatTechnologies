import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.blogs.create.validator import Validator
from tests.app.domains.common.shared_specs import ValidatorBlankFieldSpec


class TestValidator(ValidatorBlankFieldSpec):
    validator_class = Validator
    valid_kwargs = {
        "name": "My Blog",
        "author_name": "Sam Shapiro",
        "owner_id": "auth0|abc123",
        "description": "A blog about things",
    }

    @pytest.mark.asyncio
    async def test_invalid_without_name(self, db_session: AsyncSession):
        v = Validator(name="", author_name="Sam", owner_id="auth0|abc")
        assert await v.validate(db_session) is False
        assert "name" in v.errors

    @pytest.mark.asyncio
    async def test_invalid_without_author_name(self, db_session: AsyncSession):
        v = Validator(name="My Blog", author_name="", owner_id="auth0|abc")
        assert await v.validate(db_session) is False
        assert "author_name" in v.errors

    @pytest.mark.asyncio
    async def test_invalid_without_owner_id(self, db_session: AsyncSession):
        v = Validator(name="My Blog", author_name="Sam", owner_id="")
        assert await v.validate(db_session) is False
        assert "owner_id" in v.errors

    @pytest.mark.asyncio
    async def test_invalid_with_blank_whitespace_name(self, db_session: AsyncSession):
        v = Validator(name="   ", author_name="Sam", owner_id="auth0|abc")
        assert await v.validate(db_session) is False
        assert "name" in v.errors

    @pytest.mark.asyncio
    async def test_description_is_optional(self, db_session: AsyncSession):
        v = Validator(name="My Blog", author_name="Sam", owner_id="auth0|abc")
        assert await v.validate(db_session) is True

    @pytest.mark.asyncio
    async def test_collects_multiple_errors(self, db_session: AsyncSession):
        v = Validator(name="", author_name="", owner_id="")
        assert await v.validate(db_session) is False
        assert "name" in v.errors
        assert "author_name" in v.errors
        assert "owner_id" in v.errors
