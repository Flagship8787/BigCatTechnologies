from fastmcp.server.auth import AuthContext

from app.auth.token import SessionToken
from app.policies.post_policy import PostPolicy

# Permission constants for MCP tool access
POSTS_CREATE = "posts:create"


def post_auth(*permissions: str):
    """Auth check using PostPolicy.

    Takes permission strings (e.g. "admin", "posts:admin", "posts:create").
    Returns a callable (AuthContext) -> bool that checks via PostPolicy.

    Usage:
        @mcp.tool(auth=post_auth(POSTS_CREATE))
        async def my_tool(): ...
    """
    def check(ctx: AuthContext) -> bool:
        if ctx.token is None:
            return False
        session_token = SessionToken(**ctx.token.claims)
        policy = PostPolicy(token=session_token)
        return policy.has_permission(*permissions)

    return check
