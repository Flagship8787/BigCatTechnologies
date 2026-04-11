from fastmcp import FastMCP

from app.domains.posts.create.operation import Operation as CreatePostInBlog
from app.domains.posts.serializer import PostSerializer
from app.mcp.posts.permissions import post_auth, POSTS_CREATE


def register(mcp: FastMCP):

    @mcp.tool
    def hello_world() -> str:
        return {
            'hello': 'world'
        }

    @mcp.tool(auth=post_auth(POSTS_CREATE))
    async def create_post_in_blog(blog_id: str, title: str, body: str) -> dict:
        """Create a new drafted post in the specified blog."""
        post = await CreatePostInBlog().perform(blog_id=blog_id, title=title, body=body)
        return PostSerializer(post).to_json()
