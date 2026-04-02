from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.common.operation.base_operation import BaseOperation
from app.domains.common.operation.base_validator import BaseValidator
from app.domains.blogs.create.validator import Validator
from app.models.blog import Blog


class Operation(BaseOperation):
    """Creates a new blog."""

    def _validator(self, name: str, author_name: str, owner_id: str, description: str = "") -> BaseValidator:
        return Validator(name=name, author_name=author_name, owner_id=owner_id, description=description)

    async def _do_perform(self, db: AsyncSession, name: str, author_name: str, owner_id: str, description: str = "") -> dict:
        blog = Blog(name=name, description=description, author_name=author_name, owner_id=owner_id)
        db.add(blog)
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
