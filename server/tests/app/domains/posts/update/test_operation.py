import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.post import Post, PostState
from app.domains.posts.update.operation import Operation
from tests.app.domains.common.shared_specs import OperationValidationGatingSpec
from tests.conftest import create_post


class TestOperation(OperationValidationGatingSpec):
    operation_class = Operation
    invalid_kwargs = {"post": None}
    invalid_fields = ["post"]

    @pytest.mark.asyncio
    async def test_do_perform_returns_post_instance(self, db_session: AsyncSession):
        post = await create_post(db_session)

        result = await Operation()._do_perform(db_session, post=post, title="Updated Title")

        assert isinstance(result, Post)
        assert result.id == post.id

    @pytest.mark.asyncio
    async def test_do_perform_applies_title_change(self, db_session: AsyncSession):
        post = await create_post(db_session)

        result = await Operation()._do_perform(db_session, post=post, title="New Title")

        assert result.title == "New Title"

    @pytest.mark.asyncio
    async def test_do_perform_applies_body_change(self, db_session: AsyncSession):
        post = await create_post(db_session)

        result = await Operation()._do_perform(db_session, post=post, body="New body content")

        assert result.body == "New body content"

    @pytest.mark.asyncio
    async def test_do_perform_applies_state_change(self, db_session: AsyncSession):
        post = await create_post(db_session, state=PostState.drafted.value)

        result = await Operation()._do_perform(db_session, post=post, state=PostState.published.value)

        assert result.state == PostState.published.value

    @pytest.mark.asyncio
    async def test_do_perform_persists_changes(self, db_session: AsyncSession):
        from sqlalchemy import select

        post = await create_post(db_session)

        await Operation()._do_perform(db_session, post=post, title="Persisted Title")

        db_result = await db_session.execute(select(Post).where(Post.id == post.id))
        updated = db_result.scalar_one_or_none()
        assert updated.title == "Persisted Title"

    @pytest.mark.asyncio
    async def test_do_perform_does_not_change_omitted_fields(self, db_session: AsyncSession):
        post = await create_post(db_session)
        original_title = post.title
        original_body = post.body

        result = await Operation()._do_perform(db_session, post=post, state=PostState.published.value)

        assert result.title == original_title
        assert result.body == original_body
