from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import require_auth0_token
from app.auth.token import SessionToken
from app.db import get_db
from app.services import linkedin as linkedin_service


class LinkedInPostRequest(BaseModel):
    text: str


def register(app: FastAPI):

    @app.post("/social/linkedin/post")
    async def post_to_linkedin(
        body: LinkedInPostRequest,
        token: SessionToken = Depends(require_auth0_token),
        db: AsyncSession = Depends(get_db),
    ):
        """Post text to LinkedIn on behalf of the authenticated user."""
        try:
            post_urn = await linkedin_service.post_to_linkedin(db, auth0_id=token.sub, text=body.text)
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc
        except Exception as exc:
            raise HTTPException(status_code=502, detail=f"LinkedIn API error: {exc}") from exc
        return {"status": "ok", "post_urn": post_urn}
