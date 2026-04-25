from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.common.operation.base_operation import BaseOperation
from app.domains.common.operation.base_validator import BaseValidator
from app.domains.users.find_or_create.validator import Validator
from app.models.user import User


class Operation(BaseOperation):
    """Finds an existing user by auth0_id, or creates one if not found."""

    def _validator(self, auth0_id: str) -> BaseValidator:
        return Validator(auth0_id=auth0_id)

    async def _do_perform(self, db: AsyncSession, auth0_id: str) -> User:
        result = await db.execute(select(User).where(User.auth0_id == auth0_id))
        user = result.scalar_one_or_none()
        if user is not None:
            return user

        user = User(auth0_id=auth0_id)
        db.add(user)
        await db.commit()
        await db.refresh(user)
        return user
