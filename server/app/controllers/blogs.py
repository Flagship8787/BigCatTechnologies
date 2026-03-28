from typing import Optional, List
from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from pydantic import BaseModel, ConfigDict

from app.db import get_db
from app.models.blog import Blog
from app.models.post import Post


class BlogCreate(BaseModel):
    name: str
    description: str = ""


class BlogUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None


class PostResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    blog_id: str
    title: str
    body: str
    created_at: str
    updated_at: str


class BlogResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    description: str
    created_at: str
    updated_at: str


class BlogWithPostsResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    description: str
    created_at: str
    updated_at: str
    posts: List[PostResponse]


def _blog_to_response(blog: Blog) -> dict:
    return {
        "id": blog.id,
        "name": blog.name,
        "description": blog.description,
        "created_at": blog.created_at.isoformat(),
        "updated_at": blog.updated_at.isoformat(),
    }


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

    @app.post("/blogs", status_code=201)
    async def create_blog(data: BlogCreate, db: AsyncSession = Depends(get_db)):
        blog = Blog(name=data.name, description=data.description)
        db.add(blog)
        await db.commit()
        await db.refresh(blog)
        return _blog_to_response(blog)

    @app.get("/blogs")
    async def list_blogs(db: AsyncSession = Depends(get_db)):
        result = await db.execute(select(Blog).order_by(Blog.created_at.desc()))
        blogs = result.scalars().all()
        return [_blog_to_response(b) for b in blogs]

    @app.patch("/blogs/{blog_id}")
    async def update_blog(blog_id: str, data: BlogUpdate, db: AsyncSession = Depends(get_db)):
        result = await db.execute(select(Blog).where(Blog.id == blog_id))
        blog = result.scalar_one_or_none()
        if blog is None:
            raise HTTPException(status_code=404, detail="Blog not found")
        if data.name is not None:
            blog.name = data.name
        if data.description is not None:
            blog.description = data.description
        await db.commit()
        await db.refresh(blog)
        return _blog_to_response(blog)

    @app.get("/blogs/{blog_id}")
    async def get_blog(blog_id: str, db: AsyncSession = Depends(get_db)):
        result = await db.execute(
            select(Blog).where(Blog.id == blog_id).options(selectinload(Blog.posts))
        )
        blog = result.scalar_one_or_none()
        if blog is None:
            raise HTTPException(status_code=404, detail="Blog not found")
        response = _blog_to_response(blog)
        response["posts"] = [_post_to_response(p) for p in blog.posts]
        return response
