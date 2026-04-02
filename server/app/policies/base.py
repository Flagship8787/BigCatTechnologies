from abc import ABC, abstractmethod

from fastapi import HTTPException
from sqlalchemy import Select

from app.auth.token import SessionToken


class NotAuthorized(HTTPException):
    def __init__(self, detail="Forbidden"):
        super().__init__(status_code=403, detail=detail)


class BasePolicy(ABC):
    def __init__(self, token: SessionToken):
        self.scopes = token.scope.split()
        self.user_id = token.sub

    def has_scope(self, *scopes: str) -> bool:
        return any(s in self.scopes for s in scopes)

    @abstractmethod
    def scope(self, action: str) -> Select: ...
