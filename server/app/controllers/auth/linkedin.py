import os
from datetime import datetime, timezone, timedelta
from urllib.parse import urlencode

import httpx
from fastapi import FastAPI, Depends, Query
from fastapi.responses import RedirectResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.service import AuthService
from app.auth.token import SessionToken
from app.db import get_db
from app.models.social_token import SocialToken
from app.models.user import User

_bearer = HTTPBearer()
_auth_service = AuthService()

LINKEDIN_AUTH_URL = "https://www.linkedin.com/oauth/v2/authorization"
LINKEDIN_TOKEN_URL = "https://www.linkedin.com/oauth/v2/accessToken"
LINKEDIN_USERINFO_URL = "https://api.linkedin.com/v2/userinfo"
LINKEDIN_SCOPES = "openid profile email"


def register(app: FastAPI):

    @app.get("/auth/linkedin")
    async def linkedin_authorize(
        credentials: HTTPAuthorizationCredentials = Depends(_bearer),
    ):
        """Redirect the user to LinkedIn's authorization page.

        The raw BigCat JWT is embedded in the state param so the callback
        can identify the user without a server-side session.
        """
        raw_token = credentials.credentials
        # Validate token (raises 401 if invalid)
        await _auth_service.validate_token(raw_token)

        params = {
            "response_type": "code",
            "client_id": os.environ["LINKEDIN_CLIENT_ID"],
            "redirect_uri": os.environ["LINKEDIN_REDIRECT_URI"],
            "scope": LINKEDIN_SCOPES,
            "state": raw_token,
        }
        return RedirectResponse(url=f"{LINKEDIN_AUTH_URL}?{urlencode(params)}")

    @app.get("/auth/linkedin/callback")
    async def linkedin_callback(
        code: str = Query(...),
        state: str = Query(...),
        db: AsyncSession = Depends(get_db),
    ):
        """Handle the LinkedIn OAuth callback.

        Validates the BigCat JWT from state, exchanges the code for tokens,
        fetches the LinkedIn member ID, and upserts into social_tokens.
        """
        success_url = os.environ.get(
            "LINKEDIN_REDIRECT_SUCCESS_URL", "https://bigcattechnologies.com"
        )

        try:
            # Validate the BigCat JWT from state
            session_token: SessionToken = await _auth_service.validate_token(state)

            # Find the user
            result = await db.execute(
                select(User).where(User.auth0_id == session_token.sub)
            )
            user = result.scalar_one_or_none()
            if user is None:
                return RedirectResponse(url=f"{success_url}?linkedin=error")

            # Exchange code for LinkedIn tokens
            async with httpx.AsyncClient() as client:
                token_response = await client.post(
                    LINKEDIN_TOKEN_URL,
                    data={
                        "grant_type": "authorization_code",
                        "code": code,
                        "redirect_uri": os.environ["LINKEDIN_REDIRECT_URI"],
                        "client_id": os.environ["LINKEDIN_CLIENT_ID"],
                        "client_secret": os.environ["LINKEDIN_CLIENT_SECRET"],
                    },
                    headers={"Content-Type": "application/x-www-form-urlencoded"},
                )
                token_response.raise_for_status()
                token_data = token_response.json()

            access_token = token_data["access_token"]
            refresh_token = token_data.get("refresh_token")
            expires_in = token_data.get("expires_in")  # seconds
            expires_at = None
            if expires_in:
                expires_at = datetime.now(timezone.utc) + timedelta(seconds=expires_in)

            # Fetch LinkedIn member ID via userinfo endpoint
            async with httpx.AsyncClient() as client:
                userinfo_response = await client.get(
                    LINKEDIN_USERINFO_URL,
                    headers={"Authorization": f"Bearer {access_token}"},
                )
                userinfo_response.raise_for_status()
                linkedin_userinfo = userinfo_response.json()

            provider_user_id = linkedin_userinfo.get("sub")  # OpenID Connect sub claim

            # Upsert SocialToken
            result = await db.execute(
                select(SocialToken).where(
                    SocialToken.user_id == user.id,
                    SocialToken.provider == "linkedin",
                )
            )
            social_token = result.scalar_one_or_none()

            if social_token is None:
                social_token = SocialToken(
                    user_id=user.id,
                    provider="linkedin",
                    access_token=access_token,
                    refresh_token=refresh_token,
                    expires_at=expires_at,
                    provider_user_id=provider_user_id,
                )
                db.add(social_token)
            else:
                social_token.access_token = access_token
                social_token.refresh_token = refresh_token
                social_token.expires_at = expires_at
                social_token.provider_user_id = provider_user_id

            await db.commit()
            return RedirectResponse(url=f"{success_url}?linkedin=connected")

        except Exception:
            return RedirectResponse(url=f"{success_url}?linkedin=error")
