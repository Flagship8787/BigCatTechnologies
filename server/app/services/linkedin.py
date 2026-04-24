"""LinkedIn OAuth and posting service.

Shared by the HTTP controllers and MCP tool so token lookup,
refresh, and posting logic lives in one place.
"""
from __future__ import annotations

import uuid
from datetime import datetime, timezone, timedelta
from typing import Optional

import httpx
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.linkedin_config import LINKEDIN_CLIENT_ID, LINKEDIN_CLIENT_SECRET, LINKEDIN_REDIRECT_URI
from app.models.social_token import SocialToken
from app.models.user import User

try:
    from linkedin_api.clients.auth.client import AuthClient
except ImportError:
    AuthClient = None  # type: ignore[assignment,misc]

LINKEDIN_UGC_POSTS_URL = "https://api.linkedin.com/v2/ugcPosts"
LINKEDIN_USERINFO_URL = "https://api.linkedin.com/v2/userinfo"
PROVIDER = "linkedin"


def _make_auth_client() -> "AuthClient":
    return AuthClient(
        client_id=LINKEDIN_CLIENT_ID,
        client_secret=LINKEDIN_CLIENT_SECRET,
        redirect_url=LINKEDIN_REDIRECT_URI,
    )


async def upsert_user(db: AsyncSession, auth0_id: str) -> User:
    """Lazily upsert a User row by auth0_id. Returns the user."""
    result = await db.execute(select(User).where(User.auth0_id == auth0_id))
    user = result.scalar_one_or_none()
    if user is None:
        user = User(id=str(uuid.uuid4()), auth0_id=auth0_id)
        db.add(user)
        await db.commit()
        await db.refresh(user)
    return user


def build_linkedin_auth_url(user_id: str) -> str:
    """Return the LinkedIn OAuth authorization URL for the given user."""
    client = _make_auth_client()
    return client.generate_member_auth_url(
        scopes=["w_member_social", "openid", "profile"],
        state=user_id,
    )


async def exchange_code_for_token(
    db: AsyncSession,
    code: str,
    user_id: str,
) -> SocialToken:
    """Exchange an auth code for tokens and upsert a social_tokens row."""
    client = _make_auth_client()
    token_response = client.exchange_auth_code_for_access_token(code)

    access_token = token_response.access_token
    refresh_token = getattr(token_response, "refresh_token", None)
    expires_in = getattr(token_response, "expires_in", None)
    expires_at = (
        datetime.now(timezone.utc) + timedelta(seconds=expires_in)
        if expires_in
        else None
    )

    # Fetch LinkedIn member URN from /userinfo
    provider_user_id = await _fetch_linkedin_sub(access_token)

    return await _upsert_social_token(
        db,
        user_id=user_id,
        access_token=access_token,
        refresh_token=refresh_token,
        expires_at=expires_at,
        provider_user_id=provider_user_id,
    )


async def _fetch_linkedin_sub(access_token: str) -> Optional[str]:
    """Return the LinkedIn sub (member URN/ID) from the userinfo endpoint."""
    headers = {"Authorization": f"Bearer {access_token}"}
    async with httpx.AsyncClient() as client:
        response = await client.get(LINKEDIN_USERINFO_URL, headers=headers)
        response.raise_for_status()
        data = response.json()
    return data.get("sub")


async def _upsert_social_token(
    db: AsyncSession,
    *,
    user_id: str,
    access_token: str,
    refresh_token: Optional[str],
    expires_at: Optional[datetime],
    provider_user_id: Optional[str],
) -> SocialToken:
    result = await db.execute(
        select(SocialToken).where(
            SocialToken.user_id == user_id,
            SocialToken.provider == PROVIDER,
        )
    )
    token_row = result.scalar_one_or_none()
    if token_row is None:
        token_row = SocialToken(
            id=str(uuid.uuid4()),
            user_id=user_id,
            provider=PROVIDER,
        )
        db.add(token_row)

    token_row.access_token = access_token
    token_row.refresh_token = refresh_token
    token_row.expires_at = expires_at
    token_row.provider_user_id = provider_user_id

    await db.commit()
    await db.refresh(token_row)
    return token_row


async def get_token_for_user(db: AsyncSession, auth0_id: str) -> Optional[SocialToken]:
    """Return the LinkedIn SocialToken for a user, or None if not connected."""
    result = await db.execute(
        select(SocialToken)
        .join(User, SocialToken.user_id == User.id)
        .where(User.auth0_id == auth0_id, SocialToken.provider == PROVIDER)
    )
    return result.scalar_one_or_none()


async def _refresh_token_if_expired(db: AsyncSession, token_row: SocialToken) -> SocialToken:
    """If the token is expired and a refresh token exists, refresh it in place."""
    now = datetime.now(timezone.utc)
    if token_row.expires_at and token_row.expires_at <= now and token_row.refresh_token:
        client = _make_auth_client()
        refreshed = client.exchange_refresh_token_for_access_token(token_row.refresh_token)
        token_row.access_token = refreshed.access_token
        if getattr(refreshed, "refresh_token", None):
            token_row.refresh_token = refreshed.refresh_token
        expires_in = getattr(refreshed, "expires_in", None)
        token_row.expires_at = (
            datetime.now(timezone.utc) + timedelta(seconds=expires_in)
            if expires_in
            else None
        )
        await db.commit()
        await db.refresh(token_row)
    return token_row


async def post_to_linkedin(db: AsyncSession, auth0_id: str, text: str) -> str:
    """Post text to LinkedIn on behalf of the user. Returns the post URN."""
    token_row = await get_token_for_user(db, auth0_id)
    if token_row is None:
        raise ValueError("No LinkedIn token found for user. Connect LinkedIn first.")

    token_row = await _refresh_token_if_expired(db, token_row)

    member_id = token_row.provider_user_id
    payload = {
        "author": f"urn:li:person:{member_id}",
        "lifecycleState": "PUBLISHED",
        "specificContent": {
            "com.linkedin.ugc.ShareContent": {
                "shareCommentary": {"text": text},
                "shareMediaCategory": "NONE",
            }
        },
        "visibility": {
            "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
        },
    }
    headers = {
        "Authorization": f"Bearer {token_row.access_token}",
        "Content-Type": "application/json",
        "X-Restli-Protocol-Version": "2.0.0",
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(LINKEDIN_UGC_POSTS_URL, json=payload, headers=headers)
        response.raise_for_status()
        data = response.json()

    return data.get("id", "")
