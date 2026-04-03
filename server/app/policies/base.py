from abc import ABC, abstractmethod

from sqlalchemy import Select

from app.auth.token import SessionToken
from app.domains.common.errors import NotAuthorized

__all__ = ["BasePolicy", "NotAuthorized"]


class BasePolicy(ABC):
    def __init__(self, token: SessionToken):
        self.permissions = token.permissions
        self.user_id = token.sub

    def has_permission(self, *permissions: str) -> bool:
        return any(p in self.permissions for p in permissions)

    @abstractmethod
    def scope(self, action: str) -> Select: ...
