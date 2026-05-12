from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.service import AuthService
from app.domains.common.operation.base_operation import BaseOperation
from app.domains.common.operation.base_validator import BaseValidator
from app.domains.users.find_or_create.validator import Validator
from app.models.user import User


class Operation(BaseOperation):
    """Finds an existing user by auth0_id, or creates one if not found.

    Populates/updates profile fields (email, email_verified, name, picture)
    from Auth0's /userinfo endpoint on every login.
    """

    def _validator(self, auth0_id: str, access_token: str) -> BaseValidator:
        return Validator(auth0_id=auth0_id, access_token=access_token)

    async def _do_perform(self, db: AsyncSession, auth0_id: str, access_token: str) -> User:
        profile = await AuthService().get_userinfo(access_token)

        result = await db.execute(select(User).where(User.auth0_id == auth0_id))
        user = result.scalar_one_or_none()

        if user is None:
            user = User(
                auth0_id=auth0_id,
                email=profile.get("email"),
                email_verified=profile.get("email_verified"),
                name=profile.get("name"),
                picture=profile.get("picture"),
            )
            db.add(user)
        else:
            user.email = profile.get("email")
            user.email_verified = profile.get("email_verified")
            user.name = profile.get("name")
            user.picture = profile.get("picture")

        await db.commit()
        await db.refresh(user)
        return user
