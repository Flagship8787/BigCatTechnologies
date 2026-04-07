from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.common.operation.base_validator import BaseValidator
from app.models.post import Post, PostState


class Validator(BaseValidator):
    """Validates arguments for the UpdatePost operation."""

    def __init__(self, post: Post, title: Optional[str] = None, body: Optional[str] = None, state: Optional[str] = None):
        super().__init__()
        self.post = post
        self.title = title
        self.body = body
        self.state = state

    async def validate(self, db: AsyncSession) -> bool:
        if self.post is None:
            self._add_error("post", "must not be None")
            return len(self.errors) == 0

        if self.title is not None and not self.title.strip():
            self._add_error("title", "must not be blank")

        if self.body is not None and not self.body.strip():
            self._add_error("body", "must not be blank")

        if self.state is not None and self.state not in PostState._value2member_map_:
            self._add_error("state", f"'{self.state}' is not a valid state")

        return len(self.errors) == 0
