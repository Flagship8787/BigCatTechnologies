from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.common.operation.base_operation import BaseOperation
from app.domains.common.operation.base_validator import BaseValidator
from app.domains.blogs.update.validator import Validator
from app.models.blog import Blog


class Operation(BaseOperation):
    """Updates an existing blog's mutable fields."""

    def _validator(self, blog_id: str, name: str, author_name: str, description: str = "") -> BaseValidator:
        return Validator(blog_id=blog_id, name=name, author_name=author_name, description=description)

    async def _do_perform(self, db: AsyncSession, blog_id: str, name: str, author_name: str, description: str = "") -> Blog:
        result = await db.execute(select(Blog).where(Blog.id == blog_id))
        blog = result.scalar_one()

        blog.name = name
        blog.author_name = author_name
        blog.description = description

        await db.commit()
        await db.refresh(blog)
        return blog
