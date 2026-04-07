"""
Dev seed script — creates two blogs, each with two lorem ipsum posts.
Run with: python dev_seed.py

Safe to re-run: skips records that already exist by name.
"""

import asyncio
from sqlalchemy import select
from app.db import AsyncSessionLocal
from app.models import Blog, Post

LOREM_SHORT = (
    "Lorem ipsum dolor sit amet, consectetur adipiscing elit. "
    "Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua."
)

LOREM_LONG = (
    "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor "
    "incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud "
    "exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure "
    "dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. "
    "Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt "
    "mollit anim id est laborum.\n\n"
    "Sed ut perspiciatis unde omnis iste natus error sit voluptatem accusantium doloremque "
    "laudantium, totam rem aperiam eaque ipsa quae ab illo inventore veritatis et quasi "
    "architecto beatae vitae dicta sunt explicabo. Nemo enim ipsam voluptatem quia voluptas "
    "sit aspernatur aut odit aut fugit, sed quia consequuntur magni dolores eos qui ratione "
    "voluptatem sequi nesciunt."
)

SEED_DATA = [
    {
        "blog": {
            "name": "Lorem Blog One",
            "description": LOREM_SHORT,
            "author_name": "Lorem Author",
            "owner_id": "dev-seed|lorem-one",
        },
        "posts": [
            {
                "title": "Lorem Post One-A",
                "body": LOREM_LONG,
            },
            {
                "title": "Lorem Post One-B",
                "body": LOREM_LONG,
            },
        ],
    },
    {
        "blog": {
            "name": "Lorem Blog Two",
            "description": LOREM_SHORT,
            "author_name": "Ipsum Author",
            "owner_id": "dev-seed|lorem-two",
        },
        "posts": [
            {
                "title": "Lorem Post Two-A",
                "body": LOREM_LONG,
            },
            {
                "title": "Lorem Post Two-B",
                "body": LOREM_LONG,
            },
        ],
    },
]


async def get_or_create_blog(session, **kwargs) -> Blog:
    result = await session.execute(select(Blog).where(Blog.name == kwargs["name"]))
    blog = result.scalar_one_or_none()
    if not blog:
        blog = Blog(**kwargs)
        session.add(blog)
        await session.flush()
        print(f"  Created blog: {kwargs['name']}")
    else:
        print(f"  Skipped blog (already exists): {kwargs['name']}")
    return blog


async def get_or_create_post(session, blog: Blog, title: str, body: str) -> Post:
    result = await session.execute(
        select(Post).where(Post.blog_id == blog.id, Post.title == title)
    )
    post = result.scalar_one_or_none()
    if not post:
        post = Post(blog_id=blog.id, title=title, body=body)
        session.add(post)
        await session.flush()
        print(f"    Created post: {title}")
    else:
        print(f"    Skipped post (already exists): {title}")
    return post


async def seed():
    async with AsyncSessionLocal() as session:
        for entry in SEED_DATA:
            blog = await get_or_create_blog(session, **entry["blog"])
            for post_data in entry["posts"]:
                await get_or_create_post(session, blog, **post_data)

        await session.commit()
        print("\nDev seed complete.")


if __name__ == "__main__":
    asyncio.run(seed())
