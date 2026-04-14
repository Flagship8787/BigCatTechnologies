"""Tests for MCP tools — serializer and get_posts/get_post tool logic."""
import uuid
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.domains.posts.serializer import PostSerializer


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_post(**kwargs):
    post = MagicMock()
    now = datetime.now(timezone.utc)
    post.id = kwargs.get("id", str(uuid.uuid4()))
    post.blog_id = kwargs.get("blog_id", str(uuid.uuid4()))
    post.title = kwargs.get("title", "Test Title")
    post.body = kwargs.get("body", "Test Body")
    post.state = kwargs.get("state", "drafted")
    post.created_at = kwargs.get("created_at", now)
    post.updated_at = kwargs.get("updated_at", now)
    return post


def _make_access_token(permissions=None, sub="user-1"):
    token = MagicMock()
    token.claims = {
        "sub": sub,
        "scope": "",
    }
    token.permissions = permissions or []
    return token


# ---------------------------------------------------------------------------
# PostSerializer tests
# ---------------------------------------------------------------------------

class TestPostSerializer:

    def test_to_json_returns_expected_keys(self):
        result = PostSerializer(_make_post()).to_json()

        assert "id" in result
        assert "blog_id" in result
        assert "title" in result
        assert "body" in result
        assert "state" in result
        assert "created_at" in result
        assert "updated_at" in result

    def test_to_json_maps_values_correctly(self):
        now = datetime(2026, 4, 1, 12, 0, 0, tzinfo=timezone.utc)
        post = _make_post(
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
        result = PostSerializer(_make_post(created_at=now, updated_at=now)).to_json()

        assert result["created_at"] == now.isoformat()
        assert result["updated_at"] == now.isoformat()


# ---------------------------------------------------------------------------
# get_posts tool tests
# ---------------------------------------------------------------------------

class TestGetPosts:

    def _make_db_result(self, posts):
        result = MagicMock()
        result.scalars.return_value.all.return_value = posts
        return result

    @pytest.mark.asyncio
    async def test_get_posts_returns_all_posts_for_admin(self):
        post1 = _make_post(id="p1", title="First")
        post2 = _make_post(id="p2", title="Second")
        access_token = _make_access_token(permissions=["admin"])

        mock_query = MagicMock()
        mock_db = AsyncMock()
        mock_db.execute.return_value = self._make_db_result([post1, post2])
        mock_db_ctx = AsyncMock()
        mock_db_ctx.__aenter__.return_value = mock_db
        mock_db_ctx.__aexit__.return_value = False

        with patch("app.mcp.posts.tools.get_access_token", return_value=access_token), \
             patch("app.mcp.posts.tools.PostPolicy") as MockPolicy, \
             patch("app.mcp.posts.tools.AsyncSessionLocal", return_value=mock_db_ctx):

            mock_policy = MockPolicy.return_value
            mock_policy.scope.return_value = mock_query

            from app.mcp.posts import tools as mcp_tools_module
            # Access the inner function directly by rebuilding the register context
            # We test the logic by calling through a minimal FastMCP mock
            mcp = MagicMock()
            registered_tools = {}

            def capture_tool(fn_or_auth=None, **kwargs):
                if callable(fn_or_auth):
                    registered_tools[fn_or_auth.__name__] = fn_or_auth
                    return fn_or_auth
                def decorator(fn):
                    registered_tools[fn.__name__] = fn
                    return fn
                return decorator

            mcp.tool = capture_tool
            mcp_tools_module.register(mcp)

            result = await registered_tools["get_posts"]()

        assert len(result) == 2
        assert result[0]["id"] == "p1"
        assert result[1]["id"] == "p2"

    @pytest.mark.asyncio
    async def test_get_posts_filters_by_blog_id(self):
        blog_id = str(uuid.uuid4())
        post1 = _make_post(id="p1", blog_id=blog_id)
        access_token = _make_access_token(permissions=["admin"])

        mock_query = MagicMock()
        mock_query.where.return_value = mock_query
        mock_db = AsyncMock()
        mock_db.execute.return_value = self._make_db_result([post1])
        mock_db_ctx = AsyncMock()
        mock_db_ctx.__aenter__.return_value = mock_db
        mock_db_ctx.__aexit__.return_value = False

        with patch("app.mcp.posts.tools.get_access_token", return_value=access_token), \
             patch("app.mcp.posts.tools.PostPolicy") as MockPolicy, \
             patch("app.mcp.posts.tools.AsyncSessionLocal", return_value=mock_db_ctx):

            mock_policy = MockPolicy.return_value
            mock_policy.scope.return_value = mock_query

            from app.mcp.posts import tools as mcp_tools_module
            mcp = MagicMock()
            registered_tools = {}

            def capture_tool(fn_or_auth=None, **kwargs):
                if callable(fn_or_auth):
                    registered_tools[fn_or_auth.__name__] = fn_or_auth
                    return fn_or_auth
                def decorator(fn):
                    registered_tools[fn.__name__] = fn
                    return fn
                return decorator

            mcp.tool = capture_tool
            mcp_tools_module.register(mcp)

            result = await registered_tools["get_posts"](blog_id=blog_id)

        mock_query.where.assert_called_once()
        assert len(result) == 1

    @pytest.mark.asyncio
    async def test_get_posts_returns_empty_list_when_no_posts(self):
        access_token = _make_access_token(permissions=["posts:admin"])

        mock_query = MagicMock()
        mock_db = AsyncMock()
        mock_db.execute.return_value = self._make_db_result([])
        mock_db_ctx = AsyncMock()
        mock_db_ctx.__aenter__.return_value = mock_db
        mock_db_ctx.__aexit__.return_value = False

        with patch("app.mcp.posts.tools.get_access_token", return_value=access_token), \
             patch("app.mcp.posts.tools.PostPolicy") as MockPolicy, \
             patch("app.mcp.posts.tools.AsyncSessionLocal", return_value=mock_db_ctx):

            mock_policy = MockPolicy.return_value
            mock_policy.scope.return_value = mock_query

            from app.mcp.posts import tools as mcp_tools_module
            mcp = MagicMock()
            registered_tools = {}

            def capture_tool(fn_or_auth=None, **kwargs):
                if callable(fn_or_auth):
                    registered_tools[fn_or_auth.__name__] = fn_or_auth
                    return fn_or_auth
                def decorator(fn):
                    registered_tools[fn.__name__] = fn
                    return fn
                return decorator

            mcp.tool = capture_tool
            mcp_tools_module.register(mcp)

            result = await registered_tools["get_posts"]()

        assert result == []


# ---------------------------------------------------------------------------
# get_post tool tests
# ---------------------------------------------------------------------------

class TestGetPost:

    def _make_db_result(self, post):
        result = MagicMock()
        result.scalars.return_value.first.return_value = post
        return result

    @pytest.mark.asyncio
    async def test_get_post_returns_post_when_found(self):
        post = _make_post(id="post-abc", title="Found It")
        access_token = _make_access_token(permissions=["admin"])

        mock_query = MagicMock()
        mock_query.where.return_value = mock_query
        mock_db = AsyncMock()
        mock_db.execute.return_value = self._make_db_result(post)
        mock_db_ctx = AsyncMock()
        mock_db_ctx.__aenter__.return_value = mock_db
        mock_db_ctx.__aexit__.return_value = False

        with patch("app.mcp.posts.tools.get_access_token", return_value=access_token), \
             patch("app.mcp.posts.tools.PostPolicy") as MockPolicy, \
             patch("app.mcp.posts.tools.AsyncSessionLocal", return_value=mock_db_ctx):

            mock_policy = MockPolicy.return_value
            mock_policy.scope.return_value = mock_query

            from app.mcp.posts import tools as mcp_tools_module
            mcp = MagicMock()
            registered_tools = {}

            def capture_tool(fn_or_auth=None, **kwargs):
                if callable(fn_or_auth):
                    registered_tools[fn_or_auth.__name__] = fn_or_auth
                    return fn_or_auth
                def decorator(fn):
                    registered_tools[fn.__name__] = fn
                    return fn
                return decorator

            mcp.tool = capture_tool
            mcp_tools_module.register(mcp)

            result = await registered_tools["get_post"]("post-abc")

        assert result["id"] == "post-abc"
        assert result["title"] == "Found It"

    @pytest.mark.asyncio
    async def test_get_post_raises_when_not_found(self):
        access_token = _make_access_token(permissions=["admin"])

        mock_query = MagicMock()
        mock_query.where.return_value = mock_query
        mock_db = AsyncMock()
        mock_db.execute.return_value = self._make_db_result(None)
        mock_db_ctx = AsyncMock()
        mock_db_ctx.__aenter__.return_value = mock_db
        mock_db_ctx.__aexit__.return_value = False

        with patch("app.mcp.posts.tools.get_access_token", return_value=access_token), \
             patch("app.mcp.posts.tools.PostPolicy") as MockPolicy, \
             patch("app.mcp.posts.tools.AsyncSessionLocal", return_value=mock_db_ctx):

            mock_policy = MockPolicy.return_value
            mock_policy.scope.return_value = mock_query

            from app.mcp.posts import tools as mcp_tools_module
            mcp = MagicMock()
            registered_tools = {}

            def capture_tool(fn_or_auth=None, **kwargs):
                if callable(fn_or_auth):
                    registered_tools[fn_or_auth.__name__] = fn_or_auth
                    return fn_or_auth
                def decorator(fn):
                    registered_tools[fn.__name__] = fn
                    return fn
                return decorator

            mcp.tool = capture_tool
            mcp_tools_module.register(mcp)

            with pytest.raises(ValueError, match="not found"):
                await registered_tools["get_post"]("nonexistent-id")


# ---------------------------------------------------------------------------
# update_post tool tests
# ---------------------------------------------------------------------------

class TestUpdatePost:

    def _make_db_result(self, post):
        result = MagicMock()
        result.scalars.return_value.first.return_value = post
        return result

    def _registered_tools(self):
        from app.mcp.posts import tools as mcp_tools_module
        mcp = MagicMock()
        registered_tools = {}

        def capture_tool(fn_or_auth=None, **kwargs):
            if callable(fn_or_auth):
                registered_tools[fn_or_auth.__name__] = fn_or_auth
                return fn_or_auth
            def decorator(fn):
                registered_tools[fn.__name__] = fn
                return fn
            return decorator

        mcp.tool = capture_tool
        mcp_tools_module.register(mcp)
        return registered_tools

    @pytest.mark.asyncio
    async def test_update_post_updates_title_and_body(self):
        post = _make_post(id="post-abc", title="Old Title", body="Old Body", state="drafted")
        updated_post = _make_post(id="post-abc", title="New Title", body="New Body", state="drafted")
        access_token = _make_access_token(permissions=["admin"])

        mock_query = MagicMock()
        mock_query.where.return_value = mock_query
        mock_db = AsyncMock()
        mock_db.execute.return_value = self._make_db_result(post)
        mock_db_ctx = AsyncMock()
        mock_db_ctx.__aenter__.return_value = mock_db
        mock_db_ctx.__aexit__.return_value = False

        with patch("app.mcp.posts.tools.get_access_token", return_value=access_token), \
             patch("app.mcp.posts.tools.PostPolicy") as MockPolicy, \
             patch("app.mcp.posts.tools.AsyncSessionLocal", return_value=mock_db_ctx), \
             patch("app.mcp.posts.tools.UpdatePost") as MockUpdatePost:

            mock_policy = MockPolicy.return_value
            mock_policy.scope.return_value = mock_query
            MockUpdatePost.return_value.perform_in = AsyncMock(return_value=updated_post)

            result = await self._registered_tools()["update_post"]("post-abc", title="New Title", body="New Body")

        assert result["id"] == "post-abc"
        assert result["title"] == "New Title"
        assert result["body"] == "New Body"

    @pytest.mark.asyncio
    async def test_update_post_raises_when_not_found(self):
        access_token = _make_access_token(permissions=["admin"])

        mock_query = MagicMock()
        mock_query.where.return_value = mock_query
        mock_db = AsyncMock()
        mock_db.execute.return_value = self._make_db_result(None)
        mock_db_ctx = AsyncMock()
        mock_db_ctx.__aenter__.return_value = mock_db
        mock_db_ctx.__aexit__.return_value = False

        with patch("app.mcp.posts.tools.get_access_token", return_value=access_token), \
             patch("app.mcp.posts.tools.PostPolicy") as MockPolicy, \
             patch("app.mcp.posts.tools.AsyncSessionLocal", return_value=mock_db_ctx):

            mock_policy = MockPolicy.return_value
            mock_policy.scope.return_value = mock_query

            with pytest.raises(ValueError, match="not found"):
                await self._registered_tools()["update_post"]("nonexistent-id")

    @pytest.mark.asyncio
    async def test_update_post_raises_when_post_is_published(self):
        post = _make_post(id="post-abc", state="published")
        access_token = _make_access_token(permissions=["admin"])

        mock_query = MagicMock()
        mock_query.where.return_value = mock_query
        mock_db = AsyncMock()
        mock_db.execute.return_value = self._make_db_result(post)
        mock_db_ctx = AsyncMock()
        mock_db_ctx.__aenter__.return_value = mock_db
        mock_db_ctx.__aexit__.return_value = False

        with patch("app.mcp.posts.tools.get_access_token", return_value=access_token), \
             patch("app.mcp.posts.tools.PostPolicy") as MockPolicy, \
             patch("app.mcp.posts.tools.AsyncSessionLocal", return_value=mock_db_ctx):

            mock_policy = MockPolicy.return_value
            mock_policy.scope.return_value = mock_query

            with pytest.raises(ValueError, match="published"):
                await self._registered_tools()["update_post"]("post-abc", title="New Title")

    @pytest.mark.asyncio
    async def test_update_post_passes_only_provided_fields(self):
        post = _make_post(id="post-abc", title="Old Title", body="Unchanged Body", state="drafted")
        updated_post = _make_post(id="post-abc", title="New Title", body="Unchanged Body", state="drafted")
        access_token = _make_access_token(permissions=["posts:admin"])

        mock_query = MagicMock()
        mock_query.where.return_value = mock_query
        mock_db = AsyncMock()
        mock_db.execute.return_value = self._make_db_result(post)
        mock_db_ctx = AsyncMock()
        mock_db_ctx.__aenter__.return_value = mock_db
        mock_db_ctx.__aexit__.return_value = False

        with patch("app.mcp.posts.tools.get_access_token", return_value=access_token), \
             patch("app.mcp.posts.tools.PostPolicy") as MockPolicy, \
             patch("app.mcp.posts.tools.AsyncSessionLocal", return_value=mock_db_ctx), \
             patch("app.mcp.posts.tools.UpdatePost") as MockUpdatePost:

            mock_policy = MockPolicy.return_value
            mock_policy.scope.return_value = mock_query
            mock_perform = AsyncMock(return_value=updated_post)
            MockUpdatePost.return_value.perform_in = mock_perform

            await self._registered_tools()["update_post"]("post-abc", title="New Title")

        mock_perform.assert_called_once_with(mock_db, post=post, title="New Title", body=None)

    @pytest.mark.asyncio
    async def test_update_post_accessible_with_posts_admin_own(self):
        post = _make_post(id="post-abc", state="drafted")
        updated_post = _make_post(id="post-abc", state="drafted")
        access_token = _make_access_token(permissions=["posts:admin:own"])

        mock_query = MagicMock()
        mock_query.where.return_value = mock_query
        mock_db = AsyncMock()
        mock_db.execute.return_value = self._make_db_result(post)
        mock_db_ctx = AsyncMock()
        mock_db_ctx.__aenter__.return_value = mock_db
        mock_db_ctx.__aexit__.return_value = False

        with patch("app.mcp.posts.tools.get_access_token", return_value=access_token), \
             patch("app.mcp.posts.tools.PostPolicy") as MockPolicy, \
             patch("app.mcp.posts.tools.AsyncSessionLocal", return_value=mock_db_ctx), \
             patch("app.mcp.posts.tools.UpdatePost") as MockUpdatePost:

            mock_policy = MockPolicy.return_value
            mock_policy.scope.return_value = mock_query
            MockUpdatePost.return_value.perform_in = AsyncMock(return_value=updated_post)

            result = await self._registered_tools()["update_post"]("post-abc", body="New Body")

        assert result["id"] == "post-abc"
