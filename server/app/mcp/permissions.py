from fastmcp.server.auth import AuthContext

# Permission constants for MCP tool access
POSTS_CREATE = "posts:create"


def require_permissions(*permissions: str):
    """Auth check that requires ALL specified permissions to be present
    in the token's 'permissions' claim (Auth0 RBAC).

    Usage:
        @mcp.tool(auth=require_permissions(POSTS_CREATE))
        async def my_tool(): ...
    """
    required = set(permissions)

    def check(ctx: AuthContext) -> bool:
        if ctx.token is None:
            return False
        token_permissions = set(ctx.token.claims.get("permissions", []))
        return required.issubset(token_permissions)

    return check
