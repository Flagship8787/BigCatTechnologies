from fastapi import HTTPException


class NotAuthorized(HTTPException):
    def __init__(self, detail="Forbidden"):
        super().__init__(status_code=403, detail=detail)
