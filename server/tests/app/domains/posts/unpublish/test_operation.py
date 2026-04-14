import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.post import Post, PostState
from app.domains.posts.unpublish.operation import Operation
from tests.app.domains.common.shared_specs import OperationValidationGatingSpec
from tests.conftest import create_post, create_blog


class TestOperation(OperationValidationGatingSpec):
    operation_class = Operation
    invalid_kwargs = {"post": None}
    invalid_fields = ["post"]

    @pytest.mark.asyncio
    async def test_do_perform_returns_post_instance(self, db_session: AsyncSession):
        post = await create_post(db_session, state=PostState.published.value)

        result = await Operation()._do_perform(db_session, post=post)

        assert isinstance(result, Post)
        assert result.id == post.id

    @pytest.mark.asyncio
    async def test_do_perform_transitions_state_to_drafted(self, db_session: AsyncSession):
        post = await create_post(db_session, state=PostState.published.value)

        result = await Operation()._do_perform(db_session, post=post)

        assert result.state == PostState.drafted.value

    @pytest.mark.asyncio
    async def test_do_perform_persists_state_change(self, db_session: AsyncSession):
        from sqlalchemy import select

        post = await create_post(db_session, state=PostState.published.value)

        await Operation()._do_perform(db_session, post=post)

        db_result = await db_session.execute(select(Post).where(Post.id == post.id))
        updated = db_result.scalar_one_or_none()
        assert updated.state == PostState.drafted.value
