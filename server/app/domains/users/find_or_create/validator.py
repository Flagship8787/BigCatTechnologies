from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.common.operation.base_validator import BaseValidator


class Validator(BaseValidator):
    """Validates arguments for the FindOrCreateUser operation."""

    def __init__(self, auth0_id: str):
        super().__init__()
        self.auth0_id = auth0_id

    async def validate(self, db: AsyncSession) -> bool:
        if not self.auth0_id or not self.auth0_id.strip():
            self._add_error("auth0_id", "must not be blank")

        return len(self.errors) == 0
