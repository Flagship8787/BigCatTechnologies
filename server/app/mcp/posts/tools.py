from typing import Optional

from fastmcp import FastMCP
from fastmcp.server.dependencies import get_access_token

from app.auth.token import SessionToken
from app.db import AsyncSessionLocal
from app.domains.posts.create.operation import Operation as CreatePostInBlog
from app.domains.posts.update.operation import Operation as UpdatePost
from app.domains.posts.serializer import PostSerializer
from app.mcp.posts.permissions import post_auth, POSTS_CREATE
from app.models.post import Post
from app.policies.post_policy import PostPolicy

POSTS_READ = ("admin", "posts:admin", "posts:admin:own")
POSTS_UPDATE = ("admin", "posts:admin", "posts:admin:own")


def _session_token_from_access_token(access_token) -> SessionToken:
    """Build a SessionToken from a FastMCP AccessToken.

    The OAuthProxy embeds upstream Auth0 claims under `upstream_claims` in the
    FastMCP JWT payload. We prefer those when present, falling back to top-level
    claims for backwards compatibility.
    """
    if access_token is None:
        return SessionToken(sub="", scope="")
    claims = access_token.claims or {}
    upstream = claims.get("upstream_claims") or {}
    return SessionToken(
        sub=upstream.get("sub") or claims.get("sub") or "",
        scope=upstream.get("scope") or claims.get("scope") or "",
        permissions=upstream.get("permissions") or claims.get("permissions") or [],
    )


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

    @mcp.tool
    async def get_posts(blog_id: Optional[str] = None) -> list:
        """List posts. Returns only published posts for unauthenticated callers.
        Authenticated callers with read permissions see all posts."""
        access_token = get_access_token()
        policy = PostPolicy(token=_session_token_from_access_token(access_token))
        query = policy.scope("get")
        if blog_id is not None:
            query = query.where(Post.blog_id == blog_id)
        async with AsyncSessionLocal() as db:
            result = await db.execute(query)
            posts = result.scalars().all()
        return [PostSerializer(post).to_json() for post in posts]

    @mcp.tool
    async def get_post(post_id: str) -> dict:
        """Get a post by ID. Returns the post if published (no auth required),
        or if the caller has read permissions."""
        access_token = get_access_token()
        policy = PostPolicy(token=_session_token_from_access_token(access_token))
        query = policy.scope("get").where(Post.id == post_id)
        async with AsyncSessionLocal() as db:
            result = await db.execute(query)
            post = result.scalars().first()
        if post is None:
            raise ValueError(f"Post {post_id} not found")
        return PostSerializer(post).to_json()

    @mcp.tool(auth=post_auth(*POSTS_UPDATE))
    async def update_post(post_id: str, title: Optional[str] = None, body: Optional[str] = None) -> dict:
        """Update the title and/or body of a drafted post. Raises an error if the post is published."""
        access_token = get_access_token()
        policy = PostPolicy(token=_session_token_from_access_token(access_token))
        query = policy.scope("update").where(Post.id == post_id)
        async with AsyncSessionLocal() as db:
            result = await db.execute(query)
            post = result.scalars().first()
            if post is None:
                raise ValueError(f"Post {post_id} not found")
            if post.state == "published":
                raise ValueError(f"Post {post_id} is published and cannot be updated")
            updated = await UpdatePost().perform_in(db, post=post, title=title, body=body)
        return PostSerializer(updated).to_json()
