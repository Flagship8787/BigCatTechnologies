from typing import Optional

from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel

from app.db import get_db
from app.models.blog import Blog
from app.models.post import Post, PostState


class PostCreate(BaseModel):
    title: str
    body: str = ""


class PostUpdate(BaseModel):
    title: Optional[str] = None
    body: Optional[str] = None
    state: Optional[PostState] = None


def _post_to_response(post: Post) -> dict:
    return {
        "id": post.id,
        "blog_id": post.blog_id,
        "title": post.title,
        "body": post.body,
        "state": post.state,
        "created_at": post.created_at.isoformat(),
        "updated_at": post.updated_at.isoformat(),
    }


def register(app: FastAPI):

    @app.get("/posts/{post_id}")
    async def get_post(post_id: str, db: AsyncSession = Depends(get_db)):
        result = await db.execute(select(Post).where(Post.id == post_id))
        post = result.scalar_one_or_none()
        if post is None:
            raise HTTPException(status_code=404, detail="Post not found")
        return _post_to_response(post)

    @app.patch("/posts/{post_id}")
    async def update_post(post_id: str, data: PostUpdate, db: AsyncSession = Depends(get_db)):
        result = await db.execute(select(Post).where(Post.id == post_id))
        post = result.scalar_one_or_none()
        if post is None:
            raise HTTPException(status_code=404, detail="Post not found")
        if data.title is not None:
            post.title = data.title
        if data.body is not None:
            post.body = data.body
        if data.state is not None:
            post.state = data.state
        await db.commit()
        await db.refresh(post)
        return _post_to_response(post)

    @app.post("/blogs/{blog_id}/posts", status_code=201)
    async def create_post(blog_id: str, data: PostCreate, db: AsyncSession = Depends(get_db)):
        result = await db.execute(select(Blog).where(Blog.id == blog_id))
        blog = result.scalar_one_or_none()
        if blog is None:
            raise HTTPException(status_code=404, detail="Blog not found")
        post = Post(blog_id=blog_id, title=data.title, body=data.body)
        db.add(post)
        await db.commit()
        await db.refresh(post)
        return _post_to_response(post)
