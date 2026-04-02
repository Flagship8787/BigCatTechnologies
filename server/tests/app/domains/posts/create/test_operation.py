import pytest
from unittest.mock import AsyncMock, patch
from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.posts.create.operation import Operation
from app.domains.common.operation.errors import ValidationError
from app.models.post import PostState
from tests.conftest import create_blog
from tests.factories.post import PostFactory


class TestOperation:

    # -----------------------------------------------------------------------
    # _do_perform — DB logic with injected session
    # -----------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_do_perform_returns_post_data(self, db_session: AsyncSession):
        blog = await create_blog(db_session)
        post_data = PostFactory.build().__dict__

        result = await Operation()._do_perform(
            db_session,
            blog_id=blog.id,
            title=post_data["title"],
            body=post_data["body"],
        )

        assert result["blog_id"] == blog.id
        assert result["title"] == post_data["title"]
        assert result["body"] == post_data["body"]
        assert "id" in result
        assert "created_at" in result
        assert "updated_at" in result

    @pytest.mark.asyncio
    async def test_do_perform_sets_state_to_drafted(self, db_session: AsyncSession):
        blog = await create_blog(db_session)
        post_data = PostFactory.build().__dict__

        result = await Operation()._do_perform(
            db_session,
            blog_id=blog.id,
            title=post_data["title"],
            body=post_data["body"],
        )

        assert result["state"] == PostState.drafted.value

    @pytest.mark.asyncio
    async def test_do_perform_returns_error_for_unknown_blog(self, db_session: AsyncSession):
        post_data = PostFactory.build().__dict__

        result = await Operation()._do_perform(
            db_session,
            blog_id="nonexistent-blog-id",
            title=post_data["title"],
            body=post_data["body"],
        )

        assert "error" in result
        assert "nonexistent-blog-id" in result["error"]

    @pytest.mark.asyncio
    async def test_do_perform_persists_post_to_db(self, db_session: AsyncSession):
        from sqlalchemy import select
        from app.models.post import Post

        blog = await create_blog(db_session)
        post_data = PostFactory.build().__dict__

        result = await Operation()._do_perform(
            db_session,
            blog_id=blog.id,
            title=post_data["title"],
            body=post_data["body"],
        )

        db_result = await db_session.execute(select(Post).where(Post.id == result["id"]))
        post = db_result.scalar_one_or_none()
        assert post is not None
        assert post.title == post_data["title"]
        assert post.blog_id == blog.id

    # -----------------------------------------------------------------------
    # perform — validation gating
    # -----------------------------------------------------------------------

    @pytest.mark.asyncio
    async def test_perform_raises_validation_error_on_invalid_args(self):
        with pytest.raises(ValidationError) as exc_info:
            await Operation().perform(blog_id="", title="", body="valid body")

        assert "blog_id" in exc_info.value.errors
        assert "title" in exc_info.value.errors

    @pytest.mark.asyncio
    async def test_perform_does_not_touch_db_when_validation_fails(self):
        """Confirm _do_perform is never called when validation fails."""
        op = Operation()
        op._do_perform = AsyncMock()

        with pytest.raises(ValidationError):
            await op.perform(blog_id="", title="", body="")

        op._do_perform.assert_not_called()
