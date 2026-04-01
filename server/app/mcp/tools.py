from fastmcp import FastMCP
from fastmcp.server.auth import require_scopes
from sqlalchemy import select

from app.db import AsyncSessionLocal
from app.models.blog import Blog
from app.models.post import Post, PostState


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
            result = await db.execute(select(Blog).where(Blog.id == blog_id))
            blog = result.scalar_one_or_none()
            if blog is None:
                return {"error": f"Blog '{blog_id}' not found"}

            post = Post(
                blog_id=blog_id,
                title=title,
                body=body,
                state=PostState.drafted.value,
            )
            db.add(post)
            await db.commit()
            await db.refresh(post)

            return {
                "id": post.id,
                "blog_id": post.blog_id,
                "title": post.title,
                "body": post.body,
                "state": post.state,
                "created_at": post.created_at.isoformat(),
                "updated_at": post.updated_at.isoformat(),
            }
