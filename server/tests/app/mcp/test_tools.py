import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.post import PostState
from app.services.posts import create_post_in_blog
from tests.conftest import create_blog
from tests.factories.post import PostFactory


@pytest.mark.asyncio
async def test_create_post_in_blog_returns_post(db_session: AsyncSession):
    blog = await create_blog(db_session)
    post_data = PostFactory.build().__dict__

    result = await create_post_in_blog(
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
async def test_create_post_in_blog_sets_state_to_drafted(db_session: AsyncSession):
    blog = await create_blog(db_session)
    post_data = PostFactory.build().__dict__

    result = await create_post_in_blog(
        db_session,
        blog_id=blog.id,
        title=post_data["title"],
        body=post_data["body"],
    )

    assert result["state"] == PostState.drafted.value


@pytest.mark.asyncio
async def test_create_post_in_blog_returns_error_for_unknown_blog(db_session: AsyncSession):
    post_data = PostFactory.build().__dict__

    result = await create_post_in_blog(
        db_session,
        blog_id="nonexistent-blog-id",
        title=post_data["title"],
        body=post_data["body"],
    )

    assert "error" in result
    assert "nonexistent-blog-id" in result["error"]


@pytest.mark.asyncio
async def test_create_post_in_blog_persists_to_db(db_session: AsyncSession):
    from sqlalchemy import select
    from app.models.post import Post

    blog = await create_blog(db_session)
    post_data = PostFactory.build().__dict__

    result = await create_post_in_blog(
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
