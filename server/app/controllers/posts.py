from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db import get_db
from app.models.post import Post, PostState
from app.domains.posts.serializer import PostSerializer


def register(app: FastAPI):

    @app.get("/posts/{post_id}")
    async def get_post(post_id: str, db: AsyncSession = Depends(get_db)):
        result = await db.execute(select(Post).where(Post.id == post_id))
        post = result.scalar_one_or_none()
        if post is None or post.state != PostState.published.value:
            raise HTTPException(status_code=404, detail="Post not found")
        return PostSerializer(post).to_json()
