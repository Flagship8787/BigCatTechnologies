import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.post import Post, PostState
from app.domains.posts.publish.operation import Operation
from tests.app.domains.common.shared_specs import OperationValidationGatingSpec
from tests.conftest import create_post


class TestOperation(OperationValidationGatingSpec):
    operation_class = Operation
    invalid_kwargs = {"post_id": "some-id", "state": PostState.published.value}
    invalid_fields = ["state"]

    @pytest.mark.asyncio
    async def test_do_perform_returns_post_instance(self, db_session: AsyncSession):
        post = await create_post(db_session, state=PostState.drafted.value)

        result = await Operation()._do_perform(
            db_session,
            post_id=post.id,
            state=PostState.drafted.value,
        )

        assert isinstance(result, Post)
        assert result.id == post.id

    @pytest.mark.asyncio
    async def test_do_perform_transitions_state_to_published(self, db_session: AsyncSession):
        post = await create_post(db_session, state=PostState.drafted.value)

        result = await Operation()._do_perform(
            db_session,
            post_id=post.id,
            state=PostState.drafted.value,
        )

        assert result.state == PostState.published.value

    @pytest.mark.asyncio
    async def test_do_perform_persists_state_change(self, db_session: AsyncSession):
        from sqlalchemy import select

        post = await create_post(db_session, state=PostState.drafted.value)

        await Operation()._do_perform(
            db_session,
            post_id=post.id,
            state=PostState.drafted.value,
        )

        db_result = await db_session.execute(select(Post).where(Post.id == post.id))
        updated = db_result.scalar_one_or_none()
        assert updated.state == PostState.published.value
