from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.common.operation.base_operation import BaseOperation
from app.domains.common.operation.base_validator import BaseValidator
from app.domains.posts.update.validator import Validator
from app.models.post import Post


class Operation(BaseOperation):
    """Updates fields on an existing post."""

    def _validator(self, post: Post, title: Optional[str] = None, body: Optional[str] = None, state: Optional[str] = None) -> BaseValidator:
        return Validator(post=post, title=title, body=body, state=state)

    async def _do_perform(self, db: AsyncSession, post: Post, title: Optional[str] = None, body: Optional[str] = None, state: Optional[str] = None) -> Post:
        if title is not None:
            post.title = title
        if body is not None:
            post.body = body
        if state is not None:
            post.state = state
        await db.commit()
        await db.refresh(post)
        return post
