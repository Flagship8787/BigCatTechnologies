from fastapi import FastAPI, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import get_user_policy
from app.db import get_db
from app.models.user import User
from app.policies.user_policy import UserPolicy


def register(app: FastAPI):

    @app.get("/admin/users")
    async def list_users(
        db: AsyncSession = Depends(get_db),
        policy: UserPolicy = Depends(get_user_policy),
    ):
        query = policy.scope("read").order_by(User.created_at.desc())
        result = await db.execute(query)
        users = result.scalars().all()
        return [
            {
                "id": u.id,
                "auth0_id": u.auth0_id,
                "email": u.email,
                "email_verified": u.email_verified,
                "name": u.name,
                "picture": u.picture,
                "created_at": u.created_at.isoformat(),
                "updated_at": u.updated_at.isoformat(),
            }
            for u in users
        ]
