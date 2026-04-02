from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.blog import Blog
from app.models.post import Post, PostState


async def create_post_in_blog(
    db: AsyncSession,
    blog_id: str,
    title: str,
    body: str,
) -> dict:
    """Create a new drafted post in the specified blog.

    Returns a dict with the created post data, or an error dict if the blog is not found.
    """
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
