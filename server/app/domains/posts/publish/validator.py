from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.common.operation.base_validator import BaseValidator
from app.models.post import Post, PostState


class Validator(BaseValidator):
    """Validates arguments for the PublishPost operation."""

    def __init__(self, post_id: str, state: str):
        super().__init__()
        self.post_id = post_id
        self.state = state

    async def validate(self, db: AsyncSession) -> bool:
        if not self.post_id or not self.post_id.strip():
            self._add_error("post_id", "must not be blank")
        else:
            result = await db.execute(select(Post).where(Post.id == self.post_id))
            if result.scalar_one_or_none() is None:
                self._add_error("post_id", f"post '{self.post_id}' not found")

        if self.state != PostState.drafted.value:
            self._add_error("state", f"must be '{PostState.drafted.value}' to publish (got '{self.state}')")

        return len(self.errors) == 0
