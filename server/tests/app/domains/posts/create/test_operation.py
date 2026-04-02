import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.post import Post, PostState
from app.domains.posts.create.operation import Operation
from tests.app.domains.common.shared_specs import OperationValidationGatingSpec
from tests.conftest import create_blog
from tests.factories.post import PostFactory


class TestOperation(OperationValidationGatingSpec):
    operation_class = Operation
    invalid_kwargs = {"blog_id": "", "title": "", "body": "valid body"}
    invalid_fields = ["blog_id", "title"]

    @pytest.mark.asyncio
    async def test_do_perform_returns_post_instance(self, db_session: AsyncSession):
        blog = await create_blog(db_session)
        post_data = PostFactory.build().__dict__

        result = await Operation()._do_perform(
            db_session,
            blog_id=blog.id,
            title=post_data["title"],
            body=post_data["body"],
        )

        assert isinstance(result, Post)
        assert result.blog_id == blog.id
        assert result.title == post_data["title"]
        assert result.body == post_data["body"]

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

        assert result.state == PostState.drafted.value

    @pytest.mark.asyncio
    async def test_do_perform_returns_none_for_unknown_blog(self, db_session: AsyncSession):
        post_data = PostFactory.build().__dict__

        result = await Operation()._do_perform(
            db_session,
            blog_id="nonexistent-blog-id",
            title=post_data["title"],
            body=post_data["body"],
        )

        assert result is None

    @pytest.mark.asyncio
    async def test_do_perform_persists_to_db(self, db_session: AsyncSession):
        from sqlalchemy import select

        blog = await create_blog(db_session)
        post_data = PostFactory.build().__dict__

        result = await Operation()._do_perform(
            db_session,
            blog_id=blog.id,
            title=post_data["title"],
            body=post_data["body"],
        )

        db_result = await db_session.execute(select(Post).where(Post.id == result.id))
        post = db_result.scalar_one_or_none()
        assert post is not None
        assert post.title == post_data["title"]
        assert post.blog_id == blog.id
