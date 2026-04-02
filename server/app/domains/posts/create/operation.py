from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.common.operation.base_operation import BaseOperation
from app.domains.common.operation.base_validator import BaseValidator
from app.domains.posts.create.validator import Validator
from app.models.post import Post, PostState


class Operation(BaseOperation):
    """Creates a new drafted post in the specified blog."""

    def _validator(self, blog_id: str, title: str, body: str) -> BaseValidator:
        return Validator(blog_id=blog_id, title=title, body=body)

    async def _do_perform(self, db: AsyncSession, blog_id: str, title: str, body: str) -> Post:
        post = Post(
            blog_id=blog_id,
            title=title,
            body=body,
            state=PostState.drafted.value,
        )
        db.add(post)
        await db.commit()
        await db.refresh(post)
        return post
