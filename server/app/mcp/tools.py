from fastmcp import FastMCP
from fastmcp.server.auth import require_scopes

from app.db import AsyncSessionLocal
from app.services.posts import create_post_in_blog as _create_post_in_blog


def register(mcp: FastMCP):

    @mcp.tool
    def hello_world() -> str:
        return {
            'hello': 'world'
        }

    @mcp.tool(auth=require_scopes("posts:create"))
    async def create_post_in_blog(blog_id: str, title: str, body: str) -> dict:
        """Create a new drafted post in the specified blog."""
        async with AsyncSessionLocal() as db:
            return await _create_post_in_blog(db, blog_id, title, body)
