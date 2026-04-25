import os
from typing import Optional

import httpx
from fastapi import Depends, HTTPException, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import jwt, JWTError
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.deserializer import Deserializer
from app.auth.token import SessionToken
from app.db import get_db
from app.domains.users.find_or_create.operation import Operation as FindOrCreateUserOperation

_bearer = HTTPBearer()

_jwks_cache: Optional[dict] = None


async def _get_jwks() -> dict:
    global _jwks_cache
    if _jwks_cache is None:
        jwks_uri = os.environ["AUTH0_JWKS_URI"]
        async with httpx.AsyncClient() as client:
            response = await client.get(jwks_uri)
            response.raise_for_status()
            _jwks_cache = response.json()
    return _jwks_cache


async def require_auth0_token(
    credentials: HTTPAuthorizationCredentials = Security(_bearer),
    db: AsyncSession = Depends(get_db),
) -> SessionToken:
    token = credentials.credentials
    jwks = await _get_jwks()
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

    session_token = Deserializer(payload).deserialize()
    await FindOrCreateUserOperation().perform_in(db, auth0_id=session_token.sub)
    return session_token


def get_blog_policy(token: SessionToken = Depends(require_auth0_token)):
    from app.policies.blog_policy import BlogPolicy
    return BlogPolicy(token=token)


def get_post_policy(token: SessionToken = Depends(require_auth0_token)):
    from app.policies.post_policy import PostPolicy
    return PostPolicy(token=token)
