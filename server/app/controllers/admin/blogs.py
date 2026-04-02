from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.auth.dependencies import get_blog_policy
from app.db import get_db
from app.domains.blogs.serializer import BlogSerializer
from app.domains.blogs.update.operation import Operation as UpdateOperation
from app.models.blog import Blog
from app.policies.blog_policy import BlogPolicy


class UpdateBlogRequest(BaseModel):
    name: str
    author_name: str
    description: str = ""


def register(app: FastAPI):

    @app.get("/admin/blogs")
    async def list_blogs(
        db: AsyncSession = Depends(get_db),
        policy: BlogPolicy = Depends(get_blog_policy),
    ):
        policy.authorize("read")
        query = policy.scope(select(Blog).order_by(Blog.created_at.desc()))
        result = await db.execute(query)
        blogs = result.scalars().all()
        return [BlogSerializer(b).to_json() for b in blogs]

    @app.get("/admin/blogs/{blog_id}")
    async def get_blog(
        blog_id: str,
        db: AsyncSession = Depends(get_db),
        policy: BlogPolicy = Depends(get_blog_policy),
    ):
        policy.authorize("read")
        result = await db.execute(
            select(Blog).where(Blog.id == blog_id).options(selectinload(Blog.posts))
        )
        blog = result.scalar_one_or_none()
        if blog is None:
            raise HTTPException(status_code=404, detail="Blog not found")
        return BlogSerializer(blog).to_json()

    @app.patch("/admin/blogs/{blog_id}")
    async def update_blog(
        blog_id: str,
        body: UpdateBlogRequest,
        db: AsyncSession = Depends(get_db),
        policy: BlogPolicy = Depends(get_blog_policy),
    ):
        result = await db.execute(select(Blog).where(Blog.id == blog_id))
        blog = result.scalar_one_or_none()
        if blog is None:
            raise HTTPException(status_code=404, detail="Blog not found")
        policy.authorize("update", blog)
        updated_blog = await UpdateOperation().perform(
            blog_id=blog_id,
            name=body.name,
            author_name=body.author_name,
            description=body.description,
        )
        return BlogSerializer(updated_blog).to_json()
