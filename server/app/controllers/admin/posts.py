from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import get_post_policy
from app.db import get_db
from app.domains.posts.serializer import PostSerializer
from app.models.post import Post, PostState
from app.policies.post_policy import PostPolicy


def register(app: FastAPI):

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
        if post.state != PostState.drafted.value:
            raise HTTPException(status_code=422, detail="Post must be in drafted state to publish")
        post.state = PostState.published.value
        await db.commit()
        await db.refresh(post)
        return PostSerializer(post).to_json()
