from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.common.operation.base_validator import BaseValidator
from app.models.post import Post


class Validator(BaseValidator):
    """Validates arguments for the SharePostToX operation."""

    def __init__(self, post: Post):
        super().__init__()
        self.post = post

    async def validate(self, db: AsyncSession) -> bool:
        if self.post is None:
            self._add_error("post", "must not be None")

        return len(self.errors) == 0
