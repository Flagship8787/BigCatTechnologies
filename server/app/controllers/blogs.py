from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.db import get_db
from app.models.blog import Blog
from app.domains.blogs.serializer import BlogSerializer


def register(app: FastAPI):

    @app.get("/blogs")
    async def list_blogs(db: AsyncSession = Depends(get_db)):
        result = await db.execute(select(Blog).order_by(Blog.created_at.desc()))
        blogs = result.scalars().all()
        return [BlogSerializer(b).to_json(published_only=True) for b in blogs]

    @app.get("/blogs/{blog_id}")
    async def get_blog(blog_id: str, db: AsyncSession = Depends(get_db)):
        result = await db.execute(
            select(Blog).where(Blog.id == blog_id).options(selectinload(Blog.posts))
        )
        blog = result.scalar_one_or_none()
        if blog is None:
            raise HTTPException(status_code=404, detail="Blog not found")
        return BlogSerializer(blog).to_json(published_only=True)
