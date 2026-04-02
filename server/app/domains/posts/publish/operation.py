from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.common.operation.base_operation import BaseOperation
from app.domains.common.operation.base_validator import BaseValidator
from app.domains.posts.publish.validator import Validator
from app.models.post import Post, PostState


class Operation(BaseOperation):
    """Publishes a drafted post by transitioning its state to 'published'."""

    def _validator(self, post_id: str, state: str) -> BaseValidator:
        return Validator(post_id=post_id, state=state)

    async def _do_perform(self, db: AsyncSession, post_id: str, state: str) -> dict:
        result = await db.execute(select(Post).where(Post.id == post_id))
        post = result.scalar_one_or_none()
        if post is None:
            return {"error": f"Post '{post_id}' not found"}

        post.state = PostState.published.value
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
