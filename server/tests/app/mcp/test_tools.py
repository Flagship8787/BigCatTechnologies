"""Tests for MCP tool wiring.

Domain logic (operation/validator) is tested in tests/app/domains/.
These tests verify that the MCP tools correctly use operations and serializers.
"""
import pytest
from unittest.mock import AsyncMock, MagicMock

from app.domains.common.operation.errors import ValidationError
from app.domains.posts.serializer import serialize as serialize_post


class TestSerializePost:
    """Tests for the post serializer used by MCP tools."""

    def test_serialize_returns_expected_keys(self):
        from datetime import datetime, timezone
        post = MagicMock()
        post.id = "post-1"
        post.blog_id = "blog-1"
        post.title = "Test Title"
        post.body = "Test Body"
        post.state = "drafted"
        now = datetime.now(timezone.utc)
        post.created_at = now
        post.updated_at = now

        result = serialize_post(post)

        assert result["id"] == "post-1"
        assert result["blog_id"] == "blog-1"
        assert result["title"] == "Test Title"
        assert result["body"] == "Test Body"
        assert result["state"] == "drafted"
        assert "created_at" in result
        assert "updated_at" in result

    def test_serialize_formats_datetimes_as_iso(self):
        from datetime import datetime, timezone
        post = MagicMock()
        post.id = "post-1"
        post.blog_id = "blog-1"
        post.title = "T"
        post.body = "B"
        post.state = "drafted"
        now = datetime(2026, 4, 1, 12, 0, 0, tzinfo=timezone.utc)
        post.created_at = now
        post.updated_at = now

        result = serialize_post(post)

        assert result["created_at"] == now.isoformat()
        assert result["updated_at"] == now.isoformat()
