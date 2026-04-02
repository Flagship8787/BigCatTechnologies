from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.common.operation.base_operation import BaseOperation
from app.domains.common.operation.base_validator import BaseValidator
from app.domains.posts.create.validator import Validator
from app.models.blog import Blog
from app.models.post import Post, PostState


class Operation(BaseOperation):
    """Creates a new drafted post in the specified blog."""

    def _validator(self, blog_id: str, title: str, body: str) -> BaseValidator:
        return Validator(blog_id=blog_id, title=title, body=body)

    async def _do_perform(self, db: AsyncSession, blog_id: str, title: str, body: str) -> Post | None:
        result = await db.execute(select(Blog).where(Blog.id == blog_id))
        blog = result.scalar_one_or_none()
        if blog is None:
            return None

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
