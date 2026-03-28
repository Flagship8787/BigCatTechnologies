from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel

from app.db import get_db
from app.models.blog import Blog
from app.models.post import Post


class PostCreate(BaseModel):
    title: str
    body: str = ""


def _post_to_response(post: Post) -> dict:
    return {
        "id": post.id,
        "blog_id": post.blog_id,
        "title": post.title,
        "body": post.body,
        "created_at": post.created_at.isoformat(),
        "updated_at": post.updated_at.isoformat(),
    }


def register(app: FastAPI):

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
