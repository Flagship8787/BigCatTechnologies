from typing import List, Optional, Union

from pydantic import BaseModel


class TokenData(BaseModel):
    sub: str
    scope: str
    iss: Optional[str] = None
    aud: Optional[Union[str, List[str]]] = None
    exp: Optional[int] = None
    iat: Optional[int] = None


def deserialize_token(payload: dict) -> TokenData:
    return TokenData(
        sub=payload["sub"],
        scope=payload.get("scope", ""),
        iss=payload.get("iss"),
        aud=payload.get("aud"),
        exp=payload.get("exp"),
        iat=payload.get("iat"),
    )
