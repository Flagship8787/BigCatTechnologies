from fastmcp import FastMCP

from app.auth.token import SessionToken
from app.domains.posts.create.operation import Operation as CreatePostInBlog
from app.domains.posts.serializer import PostSerializer
from app.mcp.permissions import POSTS_CREATE
from app.policies.post_policy import PostPolicy


def _post_create_auth(ctx) -> bool:
    if ctx.token is None:
        return False
    token = SessionToken(**ctx.token.claims)
    policy = PostPolicy(token=token)
    return policy.has_permission("admin", "posts:admin", POSTS_CREATE)


def register(mcp: FastMCP):

    @mcp.tool
    def hello_world() -> str:
        return {
            'hello': 'world'
        }

    @mcp.tool(auth=_post_create_auth)
    async def create_post_in_blog(blog_id: str, title: str, body: str) -> dict:
        """Create a new drafted post in the specified blog."""
        post = await CreatePostInBlog().perform(blog_id=blog_id, title=title, body=body)
        return PostSerializer(post).to_json()
