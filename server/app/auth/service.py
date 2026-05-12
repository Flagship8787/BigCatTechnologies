import os
from typing import Any, Dict, Optional

import httpx
from fastapi import HTTPException
from jose import JWTError, jwt

from app.auth.deserializer import Deserializer
from app.auth.token import SessionToken


class AuthService:
    def __init__(self) -> None:
        self._jwks_cache: Optional[dict] = None

    async def get_jwks(self) -> dict:
        if self._jwks_cache is None:
            jwks_uri = os.environ["AUTH0_JWKS_URI"]
            async with httpx.AsyncClient() as client:
                response = await client.get(jwks_uri)
                response.raise_for_status()
                self._jwks_cache = response.json()
        return self._jwks_cache

    async def validate_token(self, token: str) -> SessionToken:
        jwks = await self.get_jwks()
        issuer = os.environ["AUTH0_ISSUER"]
        audience = os.environ["AUTH0_AUDIENCE"]

        try:
            unverified_header = jwt.get_unverified_header(token)
        except JWTError:
            raise HTTPException(status_code=401, detail="Invalid token header")

        rsa_key = {}
        for key in jwks.get("keys", []):
            if key.get("kid") == unverified_header.get("kid"):
                rsa_key = {
                    "kty": key["kty"],
                    "kid": key["kid"],
                    "use": key["use"],
                    "n": key["n"],
                    "e": key["e"],
                }
                break

        if not rsa_key:
            raise HTTPException(status_code=401, detail="Unable to find appropriate key")

        try:
            payload = jwt.decode(
                token,
                rsa_key,
                algorithms=["RS256"],
                audience=audience,
                issuer=issuer,
            )
        except JWTError:
            raise HTTPException(status_code=401, detail="Invalid token")

        return Deserializer(payload).deserialize()

    async def get_userinfo(self, token: str) -> Dict[str, Any]:
        issuer = os.environ["AUTH0_ISSUER"]
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{issuer}userinfo",
                headers={"Authorization": f"Bearer {token}"},
            )
            response.raise_for_status()
            return response.json()
