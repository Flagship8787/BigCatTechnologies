from fastapi import FastAPI, Depends, HTTPException
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import require_auth0_token
from app.auth.token import SessionToken
from app.db import get_db
from app.services import linkedin as linkedin_service


def register(app: FastAPI):

    @app.get("/auth/linkedin")
    async def linkedin_connect(
        token: SessionToken = Depends(require_auth0_token),
        db: AsyncSession = Depends(get_db),
    ):
        """Redirect the authenticated user to LinkedIn's OAuth authorization page."""
        user = await linkedin_service.upsert_user(db, auth0_id=token.sub)
        auth_url = linkedin_service.build_linkedin_auth_url(user_id=user.id)
        return RedirectResponse(url=auth_url)

    @app.get("/auth/linkedin/callback")
    async def linkedin_callback(
        code: str,
        state: str,
        db: AsyncSession = Depends(get_db),
    ):
        """Receive the LinkedIn OAuth callback, exchange code for tokens, and store them."""
        try:
            await linkedin_service.exchange_code_for_token(db, code=code, user_id=state)
        except Exception as exc:
            raise HTTPException(status_code=400, detail=f"LinkedIn OAuth error: {exc}") from exc
        return {"status": "ok", "message": "LinkedIn connected successfully."}
