from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import get_post_policy
from app.db import get_db
from app.domains.common.operation.errors import ValidationError
from app.domains.posts.publish.operation import Operation as PublishOperation
from app.domains.posts.serializer import PostSerializer
from app.models.post import Post
from app.policies.post_policy import PostPolicy


def register(app: FastAPI):

    @app.get("/admin/posts/{post_id}")
    async def get_post(
        post_id: str,
        db: AsyncSession = Depends(get_db),
        policy: PostPolicy = Depends(get_post_policy),
    ):
        query = policy.scope("get").where(Post.id == post_id)
        result = await db.execute(query)
        post = result.scalar_one_or_none()
        if post is None:
            raise HTTPException(status_code=404, detail="Post not found")
        return PostSerializer(post).to_json()

    @app.post("/admin/posts/{post_id}/publish")
    async def publish_post(
        post_id: str,
        db: AsyncSession = Depends(get_db),
        policy: PostPolicy = Depends(get_post_policy),
    ):
        query = policy.scope("publish").where(Post.id == post_id)
        result = await db.execute(query)
        post = result.scalar_one_or_none()
        if post is None:
            raise HTTPException(status_code=404, detail="Post not found")
        try:
            published_post = await PublishOperation().perform_in(db, post=post)
        except ValidationError as e:
            state_errors = e.errors.get("state", [])
            detail = state_errors[0] if state_errors else "Invalid post state"
            raise HTTPException(status_code=422, detail=detail)
        return PostSerializer(published_post).to_json()
