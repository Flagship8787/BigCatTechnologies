from abc import ABC, abstractmethod

from sqlalchemy import Select

from app.auth.token import SessionToken
from app.domains.common.errors import NotAuthorized

__all__ = ["BasePolicy", "NotAuthorized"]


class BasePolicy(ABC):
    def __init__(self, token: SessionToken):
        self.scopes = token.scope.split()
        self.user_id = token.sub

    def has_scope(self, *scopes: str) -> bool:
        return any(s in self.scopes for s in scopes)

    @abstractmethod
    def scope(self, action: str) -> Select: ...
