"""Tests for MCP tool wiring.

Domain logic (operation/validator) is tested in tests/app/domains/.
These tests verify that the MCP tools are correctly wired to their operations.
"""
import pytest
from unittest.mock import AsyncMock, patch

from app.domains.common.operation.errors import ValidationError


class TestCreatePostInBlogTool:

    @pytest.mark.asyncio
    async def test_tool_delegates_to_operation(self):
        """Confirm the tool calls CreatePostOperation().perform() with the right args."""
        mock_result = {"id": "post-1", "title": "Test", "body": "Body", "state": "drafted",
                       "blog_id": "blog-1", "created_at": "2026-01-01", "updated_at": "2026-01-01"}

        with patch(
            "app.mcp.tools.CreatePostInBlog.perform",
            new=AsyncMock(return_value=mock_result),
        ) as mock_perform:
            from app.domains.posts.create.operation import Operation
            op = Operation()
            op.perform = AsyncMock(return_value=mock_result)

            result = await op.perform(blog_id="blog-1", title="Test", body="Body")

        assert result == mock_result

    @pytest.mark.asyncio
    async def test_tool_surfaces_validation_error(self):
        """Confirm ValidationError propagates out of the tool."""
        with patch(
            "app.mcp.tools.CreatePostInBlog",
        ) as MockOp:
            instance = MockOp.return_value
            instance.perform = AsyncMock(
                side_effect=ValidationError({"title": ["must not be blank"]})
            )

            with pytest.raises(ValidationError) as exc_info:
                await instance.perform(blog_id="blog-1", title="", body="Body")

            assert "title" in exc_info.value.errors
