from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.common.operation.base_validator import BaseValidator


class Validator(BaseValidator):
    """Validates arguments for the CreateBlog operation."""

    def __init__(self, name: str, author_name: str, owner_id: str, description: str = ""):
        super().__init__()
        self.name = name
        self.author_name = author_name
        self.owner_id = owner_id
        self.description = description

    async def validate(self, db: AsyncSession) -> bool:
        if not self.name or not self.name.strip():
            self._add_error("name", "must not be blank")

        if not self.author_name or not self.author_name.strip():
            self._add_error("author_name", "must not be blank")

        if not self.owner_id or not self.owner_id.strip():
            self._add_error("owner_id", "must not be blank")

        return len(self.errors) == 0
