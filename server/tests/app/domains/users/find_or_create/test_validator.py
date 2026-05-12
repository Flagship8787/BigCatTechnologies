import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.users.find_or_create.validator import Validator
from tests.app.domains.common.shared_specs import ValidatorBlankFieldSpec

VALID_ACCESS_TOKEN = "mock.access.token"


class TestValidator(ValidatorBlankFieldSpec):
    validator_class = Validator
    valid_kwargs = {"auth0_id": "auth0|abc123", "access_token": VALID_ACCESS_TOKEN}

    @pytest.mark.asyncio
    async def test_valid_with_auth0_id(self, db_session: AsyncSession):
        v = Validator(auth0_id="auth0|abc123", access_token=VALID_ACCESS_TOKEN)
        assert await v.validate(db_session) is True
        assert v.errors == {}

    @pytest.mark.asyncio
    async def test_valid_attribute_is_true_on_success(self, db_session: AsyncSession):
        v = Validator(auth0_id="auth0|abc123", access_token=VALID_ACCESS_TOKEN)
        await v.validate(db_session)
        assert v.valid is True

    @pytest.mark.asyncio
    async def test_errors_are_empty_on_success(self, db_session: AsyncSession):
        v = Validator(auth0_id="auth0|abc123", access_token=VALID_ACCESS_TOKEN)
        await v.validate(db_session)
        assert v.errors == {}

    @pytest.mark.asyncio
    async def test_invalid_with_empty_auth0_id(self, db_session: AsyncSession):
        v = Validator(auth0_id="", access_token=VALID_ACCESS_TOKEN)
        assert await v.validate(db_session) is False
        assert "auth0_id" in v.errors

    @pytest.mark.asyncio
    async def test_invalid_with_blank_whitespace_auth0_id(self, db_session: AsyncSession):
        v = Validator(auth0_id="   ", access_token=VALID_ACCESS_TOKEN)
        assert await v.validate(db_session) is False
        assert "auth0_id" in v.errors

    @pytest.mark.asyncio
    async def test_invalid_with_empty_access_token(self, db_session: AsyncSession):
        v = Validator(auth0_id="auth0|abc123", access_token="")
        assert await v.validate(db_session) is False
        assert "access_token" in v.errors

    @pytest.mark.asyncio
    async def test_invalid_with_blank_whitespace_access_token(self, db_session: AsyncSession):
        v = Validator(auth0_id="auth0|abc123", access_token="   ")
        assert await v.validate(db_session) is False
        assert "access_token" in v.errors
