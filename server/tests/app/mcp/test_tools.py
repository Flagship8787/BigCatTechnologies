"""Tests for MCP tool operations and validators.

We test two layers:
  1. The Validator directly — fast, no DB
  2. The Operation._do_perform directly — uses the test db_session
"""
import pytest
from unittest.mock import AsyncMock, patch
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.post import PostState
from app.domains.posts.create.operation import Operation as CreatePostOperation
from app.domains.posts.create.validator import Validator as CreatePostValidator
from app.domains.common.operation.errors import ValidationError
from tests.conftest import create_blog
from tests.factories.post import PostFactory


# ---------------------------------------------------------------------------
# Validator tests
# ---------------------------------------------------------------------------

class TestCreatePostValidator:

    def test_valid_with_all_fields(self):
        v = CreatePostValidator(blog_id="some-id", title="My Title", body="Some body")
        assert v.validate() is True
        assert v.errors == {}

    def test_invalid_without_blog_id(self):
        v = CreatePostValidator(blog_id="", title="My Title", body="Some body")
        assert v.validate() is False
        assert "blog_id" in v.errors

    def test_invalid_without_title(self):
        v = CreatePostValidator(blog_id="some-id", title="", body="Some body")
        assert v.validate() is False
        assert "title" in v.errors

    def test_invalid_without_body(self):
        v = CreatePostValidator(blog_id="some-id", title="My Title", body="")
        assert v.validate() is False
        assert "body" in v.errors

    def test_invalid_with_blank_whitespace_title(self):
        v = CreatePostValidator(blog_id="some-id", title="   ", body="Some body")
        assert v.validate() is False
        assert "title" in v.errors

    def test_collects_multiple_errors(self):
        v = CreatePostValidator(blog_id="", title="", body="")
        assert v.validate() is False
        assert "blog_id" in v.errors
        assert "title" in v.errors
        assert "body" in v.errors


# ---------------------------------------------------------------------------
# Operation._do_perform tests (with injected db_session)
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_do_perform_returns_post(db_session: AsyncSession):
    blog = await create_blog(db_session)
    post_data = PostFactory.build().__dict__

    result = await CreatePostOperation()._do_perform(
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
async def test_do_perform_sets_state_to_drafted(db_session: AsyncSession):
    blog = await create_blog(db_session)
    post_data = PostFactory.build().__dict__

    result = await CreatePostOperation()._do_perform(
        db_session,
        blog_id=blog.id,
        title=post_data["title"],
        body=post_data["body"],
    )

    assert result["state"] == PostState.drafted.value


@pytest.mark.asyncio
async def test_do_perform_returns_error_for_unknown_blog(db_session: AsyncSession):
    post_data = PostFactory.build().__dict__

    result = await CreatePostOperation()._do_perform(
        db_session,
        blog_id="nonexistent-blog-id",
        title=post_data["title"],
        body=post_data["body"],
    )

    assert "error" in result
    assert "nonexistent-blog-id" in result["error"]


@pytest.mark.asyncio
async def test_do_perform_persists_to_db(db_session: AsyncSession):
    from sqlalchemy import select
    from app.models.post import Post

    blog = await create_blog(db_session)
    post_data = PostFactory.build().__dict__

    result = await CreatePostOperation()._do_perform(
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


# ---------------------------------------------------------------------------
# Operation.perform — validation gating
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_perform_raises_validation_error_on_invalid_args():
    with pytest.raises(ValidationError) as exc_info:
        await CreatePostOperation().perform(blog_id="", title="", body="valid body")

    assert "blog_id" in exc_info.value.errors
    assert "title" in exc_info.value.errors
