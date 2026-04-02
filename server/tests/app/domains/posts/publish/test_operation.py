import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.posts.publish.operation import Operation
from app.models.post import PostState
from tests.app.domains.common.shared_specs import OperationValidationGatingSpec
from tests.conftest import create_post


class TestOperation(OperationValidationGatingSpec):
    operation_class = Operation
    invalid_kwargs = {"post_id": "some-id", "state": PostState.published.value}
    invalid_fields = ["state"]

    @pytest.mark.asyncio
    async def test_do_perform_transitions_state_to_published(self, db_session: AsyncSession):
        post = await create_post(db_session, state=PostState.drafted.value)

        result = await Operation()._do_perform(
            db_session,
            post_id=post.id,
            state=PostState.drafted.value,
        )

        assert result["state"] == PostState.published.value

    @pytest.mark.asyncio
    async def test_do_perform_persists_state_change(self, db_session: AsyncSession):
        from sqlalchemy import select
        from app.models.post import Post

        post = await create_post(db_session, state=PostState.drafted.value)

        await Operation()._do_perform(
            db_session,
            post_id=post.id,
            state=PostState.drafted.value,
        )

        db_result = await db_session.execute(select(Post).where(Post.id == post.id))
        updated = db_result.scalar_one_or_none()
        assert updated.state == PostState.published.value

    @pytest.mark.asyncio
    async def test_do_perform_returns_full_post_data(self, db_session: AsyncSession):
        post = await create_post(db_session)

        result = await Operation()._do_perform(
            db_session,
            post_id=post.id,
            state=PostState.drafted.value,
        )

        assert result["id"] == post.id
        assert result["blog_id"] == post.blog_id
        assert result["title"] == post.title
        assert "created_at" in result
        assert "updated_at" in result

    @pytest.mark.asyncio
    async def test_do_perform_returns_error_for_unknown_post(self, db_session: AsyncSession):
        result = await Operation()._do_perform(
            db_session,
            post_id="nonexistent-post-id",
            state=PostState.drafted.value,
        )

        assert "error" in result
        assert "nonexistent-post-id" in result["error"]
