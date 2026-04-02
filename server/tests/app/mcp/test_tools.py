"""Tests for MCP tool wiring — primarily tests the PostSerializer."""
from datetime import datetime, timezone
from unittest.mock import MagicMock

from app.domains.posts.serializer import PostSerializer


class TestPostSerializer:

    def _make_post(self, **kwargs):
        post = MagicMock()
        now = datetime.now(timezone.utc)
        post.id = kwargs.get("id", "post-1")
        post.blog_id = kwargs.get("blog_id", "blog-1")
        post.title = kwargs.get("title", "Test Title")
        post.body = kwargs.get("body", "Test Body")
        post.state = kwargs.get("state", "drafted")
        post.created_at = kwargs.get("created_at", now)
        post.updated_at = kwargs.get("updated_at", now)
        return post

    def test_to_json_returns_expected_keys(self):
        result = PostSerializer(self._make_post()).to_json()

        assert "id" in result
        assert "blog_id" in result
        assert "title" in result
        assert "body" in result
        assert "state" in result
        assert "created_at" in result
        assert "updated_at" in result

    def test_to_json_maps_values_correctly(self):
        now = datetime(2026, 4, 1, 12, 0, 0, tzinfo=timezone.utc)
        post = self._make_post(
            id="post-123",
            blog_id="blog-456",
            title="My Title",
            body="My Body",
            state="drafted",
            created_at=now,
            updated_at=now,
        )

        result = PostSerializer(post).to_json()

        assert result["id"] == "post-123"
        assert result["blog_id"] == "blog-456"
        assert result["title"] == "My Title"
        assert result["body"] == "My Body"
        assert result["state"] == "drafted"

    def test_to_json_formats_datetimes_as_iso(self):
        now = datetime(2026, 4, 1, 12, 0, 0, tzinfo=timezone.utc)
        result = PostSerializer(self._make_post(created_at=now, updated_at=now)).to_json()

        assert result["created_at"] == now.isoformat()
        assert result["updated_at"] == now.isoformat()
