from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.common.operation.base_validator import BaseValidator
from app.models.blog import Blog


class Validator(BaseValidator):
    """Validates arguments for the CreatePostInBlog operation."""

    def __init__(self, blog_id: str, title: str, body: str):
        super().__init__()
        self.blog_id = blog_id
        self.title = title
        self.body = body

    async def validate(self, db: AsyncSession) -> bool:
        if not self.blog_id or not self.blog_id.strip():
            self._add_error("blog_id", "must not be blank")
        else:
            result = await db.execute(select(Blog).where(Blog.id == self.blog_id))
            if result.scalar_one_or_none() is None:
                self._add_error("blog_id", f"blog '{self.blog_id}' not found")

        if not self.title or not self.title.strip():
            self._add_error("title", "must not be blank")

        if not self.body or not self.body.strip():
            self._add_error("body", "must not be blank")

        return len(self.errors) == 0
