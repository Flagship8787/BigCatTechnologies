from fastapi import HTTPException
from sqlalchemy import Select

from app.auth.token import TokenData


class NotAuthorized(HTTPException):
    def __init__(self, detail="Forbidden"):
        super().__init__(status_code=403, detail=detail)


class BasePolicy:
    def __init__(self, token: TokenData):
        self.scopes = token.scope.split()
        self.user_id = token.sub

    def has_scope(self, *scopes: str) -> bool:
        return any(s in self.scopes for s in scopes)

    def scope(self, action: str) -> Select:
        """Return a base query scoped to what this user can access for the given action.

        Subclasses must implement this. Raises NotAuthorized if the user cannot
        perform the action at all; otherwise returns a Select that callers can
        chain additional .where() / .options() clauses onto before execution.
        """
        raise NotImplementedError
