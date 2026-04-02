import pytest
from datetime import datetime, timezone
from unittest.mock import MagicMock

from app.domains.blogs.serializer import BlogSerializer
from app.models.post import PostState


def _make_post(state: str = PostState.published.value, **kwargs):
    post = MagicMock()
    now = datetime.now(timezone.utc)
    post.id = kwargs.get("id", "post-1")
    post.blog_id = kwargs.get("blog_id", "blog-1")
    post.title = kwargs.get("title", "Test Post")
    post.body = kwargs.get("body", "Body text")
    post.state = state
    post.created_at = now
    post.updated_at = now
    return post


def _make_blog(posts=None, **kwargs):
    blog = MagicMock()
    now = datetime.now(timezone.utc)
    blog.id = kwargs.get("id", "blog-1")
    blog.name = kwargs.get("name", "My Blog")
    blog.description = kwargs.get("description", "A blog")
    blog.author_name = kwargs.get("author_name", "Sam")
    blog.owner_id = kwargs.get("owner_id", "auth0|123")
    blog.created_at = now
    blog.updated_at = now
    blog.posts = posts if posts is not None else []
    return blog


class TestBlogSerializer:

    def test_to_json_returns_expected_keys(self):
        blog = _make_blog()
        result = BlogSerializer(blog).to_json()

        assert "id" in result
        assert "name" in result
        assert "description" in result
        assert "author_name" in result
        assert "owner_id" in result
        assert "created_at" in result
        assert "updated_at" in result

    def test_to_json_maps_values_correctly(self):
        blog = _make_blog(name="Tech Blog", author_name="Sam", owner_id="auth0|abc")
        result = BlogSerializer(blog).to_json()

        assert result["name"] == "Tech Blog"
        assert result["author_name"] == "Sam"
        assert result["owner_id"] == "auth0|abc"

    def test_to_json_includes_all_posts_by_default(self):
        posts = [
            _make_post(state=PostState.published.value),
            _make_post(state=PostState.drafted.value, id="post-2"),
            _make_post(state=PostState.deleted.value, id="post-3"),
        ]
        blog = _make_blog(posts=posts)

        result = BlogSerializer(blog).to_json()

        assert len(result["posts"]) == 3

    def test_to_json_with_published_only_filters_to_published(self):
        posts = [
            _make_post(state=PostState.published.value, id="pub-1"),
            _make_post(state=PostState.drafted.value, id="draft-1"),
            _make_post(state=PostState.deleted.value, id="del-1"),
        ]
        blog = _make_blog(posts=posts)

        result = BlogSerializer(blog).to_json(published_only=True)

        assert len(result["posts"]) == 1
        assert result["posts"][0]["id"] == "pub-1"

    def test_to_json_with_published_only_returns_empty_list_when_none_published(self):
        posts = [
            _make_post(state=PostState.drafted.value),
            _make_post(state=PostState.deleted.value, id="post-2"),
        ]
        blog = _make_blog(posts=posts)

        result = BlogSerializer(blog).to_json(published_only=True)

        assert result["posts"] == []

    def test_to_json_without_posts_attribute_omits_posts_key(self):
        blog = MagicMock(spec=[
            "id", "name", "description", "author_name", "owner_id",
            "created_at", "updated_at"
        ])
        now = datetime.now(timezone.utc)
        blog.id = "blog-1"
        blog.name = "My Blog"
        blog.description = ""
        blog.author_name = "Sam"
        blog.owner_id = "auth0|123"
        blog.created_at = now
        blog.updated_at = now

        result = BlogSerializer(blog).to_json()

        assert "posts" not in result
