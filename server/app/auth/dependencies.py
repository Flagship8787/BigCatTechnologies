import os

from fastapi import Depends, HTTPException, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.service import AuthService
from app.auth.token import SessionToken
from app.db import get_db
from app.domains.users.find_or_create.operation import Operation as FindOrCreateUserOperation

_bearer = HTTPBearer()
_auth_service = AuthService()


async def require_auth0_token(
    credentials: HTTPAuthorizationCredentials = Security(_bearer),
    db: AsyncSession = Depends(get_db),
) -> SessionToken:
    token = credentials.credentials
    session_token = await _auth_service.validate_token(token)
    await FindOrCreateUserOperation().perform_in(db, auth0_id=session_token.sub, access_token=token)
    return session_token


def get_blog_policy(token: SessionToken = Depends(require_auth0_token)):
    from app.policies.blog_policy import BlogPolicy
    return BlogPolicy(token=token)


def get_post_policy(token: SessionToken = Depends(require_auth0_token)):
    from app.policies.post_policy import PostPolicy
    return PostPolicy(token=token)


def get_user_policy(token: SessionToken = Depends(require_auth0_token)):
    from app.policies.user_policy import UserPolicy
    return UserPolicy(token=token)
