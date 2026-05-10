from fastapi import FastAPI, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import require_auth0_token
from app.auth.token import SessionToken
from app.db import get_db
from app.models.user import User


def register(app: FastAPI):

    @app.get("/admin/users")
    async def list_users(
        db: AsyncSession = Depends(get_db),
        token: SessionToken = Depends(require_auth0_token),
    ):
        query = select(User).order_by(User.created_at.desc())
        result = await db.execute(query)
        users = result.scalars().all()
        return [
            {
                "id": u.id,
                "auth0_id": u.auth0_id,
                "created_at": u.created_at.isoformat(),
                "updated_at": u.updated_at.isoformat(),
            }
            for u in users
        ]
