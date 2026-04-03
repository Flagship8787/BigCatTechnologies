from fastmcp import FastMCP
from fastmcp.server.auth import AuthContext

from app.domains.posts.create.operation import Operation as CreatePostInBlog
from app.domains.posts.serializer import PostSerializer


def require_permissions(*permissions: str):
    """Auth check that requires ALL specified permissions to be present
    in the token's 'permissions' claim (Auth0 RBAC)."""
    required = set(permissions)

    def check(ctx: AuthContext) -> bool:
        if ctx.token is None:
            return False
        token_permissions = set(ctx.token.claims.get("permissions", []))
        return required.issubset(token_permissions)

    return check


def register(mcp: FastMCP):

    @mcp.tool
    def hello_world() -> str:
        return {
            'hello': 'world'
        }

    @mcp.tool(auth=require_permissions("posts:create"))
    async def create_post_in_blog(blog_id: str, title: str, body: str) -> dict:
        """Create a new drafted post in the specified blog."""
        post = await CreatePostInBlog().perform(blog_id=blog_id, title=title, body=body)
        return PostSerializer(post).to_json()
