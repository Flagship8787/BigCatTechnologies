from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.common.operation.base_operation import BaseOperation
from app.domains.common.operation.base_validator import BaseValidator
from app.domains.posts.publish.validator import Validator
from app.models.post import Post, PostState


class Operation(BaseOperation):
    """Publishes a drafted post by transitioning its state to 'published'."""

    def _validator(self, post: Post) -> BaseValidator:
        return Validator(post=post)

    async def _do_perform(self, db: AsyncSession, post: Post) -> Post:
        post.state = PostState.published.value
        await db.commit()
        await db.refresh(post)
        return post
