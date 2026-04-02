from typing import List, Optional, Union

from pydantic import BaseModel


class TokenData(BaseModel):
    sub: str
    scope: str
    iss: Optional[str] = None
    aud: Optional[Union[str, List[str]]] = None
    exp: Optional[int] = None
    iat: Optional[int] = None

