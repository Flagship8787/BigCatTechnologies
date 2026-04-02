from fastapi import HTTPException
from sqlalchemy import Select


class NotAuthorized(HTTPException):
    def __init__(self, detail="Forbidden"):
        super().__init__(status_code=403, detail=detail)


class BasePolicy:
    def __init__(self, scopes: list[str], user_id: str):
        self.scopes = scopes
        self.user_id = user_id

    def has_scope(self, *scopes: str) -> bool:
        return any(s in self.scopes for s in scopes)

    def authorize(self, action: str, record=None):
        if not self._can(action, record):
            raise NotAuthorized()

    def scope(self, query: Select) -> Select:
        raise NotImplementedError

    def _can(self, action: str, record=None) -> bool:
        raise NotImplementedError
