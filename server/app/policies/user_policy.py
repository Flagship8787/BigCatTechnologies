from sqlalchemy import select

from app.models.user import User
from app.policies.base import BasePolicy, NotAuthorized


class UserPolicy(BasePolicy):
    FULL_ACCESS = ("admin",)

    def scope(self, action: str):
        if action == "read":
            if self.has_permission(*self.FULL_ACCESS):
                return select(User)
            raise NotAuthorized()

        raise NotAuthorized()
