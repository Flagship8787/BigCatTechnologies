import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.posts.publish.validator import Validator
from app.models.post import PostState
from tests.app.domains.common.shared_specs import ValidatorBlankFieldSpec
from tests.conftest import create_post


class TestValidator(ValidatorBlankFieldSpec):
    validator_class = Validator
    valid_kwargs = {"post_id": "placeholder", "state": PostState.drafted.value}

    @pytest.mark.asyncio
    async def test_valid_with_all_fields(self, db_session: AsyncSession):
        post = await create_post(db_session)
        v = Validator(post_id=post.id, state=PostState.drafted.value)
        assert await v.validate(db_session) is True
        assert v.errors == {}

    @pytest.mark.asyncio
    async def test_invalid_without_post_id(self, db_session: AsyncSession):
        v = Validator(post_id="", state=PostState.drafted.value)
        assert await v.validate(db_session) is False
        assert "post_id" in v.errors

    @pytest.mark.asyncio
    async def test_invalid_with_nonexistent_post_id(self, db_session: AsyncSession):
        v = Validator(post_id="nonexistent-id", state=PostState.drafted.value)
        assert await v.validate(db_session) is False
        assert "post_id" in v.errors

    @pytest.mark.asyncio
    async def test_invalid_when_state_is_published(self, db_session: AsyncSession):
        post = await create_post(db_session)
        v = Validator(post_id=post.id, state=PostState.published.value)
        assert await v.validate(db_session) is False
        assert "state" in v.errors

    @pytest.mark.asyncio
    async def test_invalid_when_state_is_deleted(self, db_session: AsyncSession):
        post = await create_post(db_session)
        v = Validator(post_id=post.id, state=PostState.deleted.value)
        assert await v.validate(db_session) is False
        assert "state" in v.errors

    @pytest.mark.asyncio
    async def test_error_message_mentions_required_state(self, db_session: AsyncSession):
        post = await create_post(db_session)
        v = Validator(post_id=post.id, state=PostState.published.value)
        await v.validate(db_session)
        assert any(PostState.drafted.value in msg for msg in v.errors["state"])

    @pytest.mark.asyncio
    async def test_collects_multiple_errors(self, db_session: AsyncSession):
        v = Validator(post_id="", state=PostState.published.value)
        assert await v.validate(db_session) is False
        assert "post_id" in v.errors
        assert "state" in v.errors
