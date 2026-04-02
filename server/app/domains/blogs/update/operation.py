from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.common.operation.base_operation import BaseOperation
from app.domains.common.operation.base_validator import BaseValidator
from app.domains.blogs.update.validator import Validator
from app.models.blog import Blog


class Operation(BaseOperation):
    """Updates an existing blog's mutable fields."""

    def _validator(self, blog_id: str, name: str | None = None, description: str | None = None, author_name: str | None = None) -> BaseValidator:
        return Validator(blog_id=blog_id, name=name, description=description, author_name=author_name)

    async def _do_perform(self, db: AsyncSession, blog_id: str, name: str | None = None, description: str | None = None, author_name: str | None = None) -> dict:
        result = await db.execute(select(Blog).where(Blog.id == blog_id))
        blog = result.scalar_one_or_none()
        if blog is None:
            return {"error": f"Blog '{blog_id}' not found"}

        if name is not None:
            blog.name = name
        if description is not None:
            blog.description = description
        if author_name is not None:
            blog.author_name = author_name

        await db.commit()
        await db.refresh(blog)

        return {
            "id": blog.id,
            "name": blog.name,
            "description": blog.description,
            "author_name": blog.author_name,
            "owner_id": blog.owner_id,
            "created_at": blog.created_at.isoformat(),
            "updated_at": blog.updated_at.isoformat(),
        }
