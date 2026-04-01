import pytest
import httpx
from fastapi import FastAPI

from tests.factories import BlogFactory, PostFactory


def _blog_payload(blog_data: dict) -> dict:
    return {
        "name": blog_data["name"],
        "description": blog_data["description"],
        "author_name": blog_data["author_name"],
        "owner_id": blog_data["owner_id"],
    }


@pytest.mark.asyncio
async def test_create_post_returns_201(app: FastAPI):
    blog_data = BlogFactory.stub().__dict__
    post_data = PostFactory.stub().__dict__
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app), base_url="http://test"
    ) as client:
        blog = await client.post("/blogs", json=_blog_payload(blog_data))
        blog_id = blog.json()["id"]
        response = await client.post(
            f"/blogs/{blog_id}/posts",
            json={"title": post_data["title"], "body": post_data["body"]}
        )

    assert response.status_code == 201


@pytest.mark.asyncio
async def test_create_post_returns_post_data(app: FastAPI):
    blog_data = BlogFactory.stub().__dict__
    post_data = PostFactory.stub().__dict__
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app), base_url="http://test"
    ) as client:
        blog = await client.post("/blogs", json=_blog_payload(blog_data))
        blog_id = blog.json()["id"]
        response = await client.post(
            f"/blogs/{blog_id}/posts",
            json={"title": post_data["title"], "body": post_data["body"]}
        )

    body = response.json()
    assert body["title"] == post_data["title"]
    assert body["body"] == post_data["body"]
    assert body["blog_id"] == blog_id
    assert "id" in body
    assert "created_at" in body
    assert "updated_at" in body


@pytest.mark.asyncio
async def test_create_post_returns_404_for_unknown_blog(app: FastAPI):
    post_data = PostFactory.stub().__dict__
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.post(
            "/blogs/nonexistent-id/posts",
            json={"title": post_data["title"], "body": post_data["body"]}
        )

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_get_post_returns_200(app: FastAPI):
    blog_data = BlogFactory.stub().__dict__
    post_data = PostFactory.stub().__dict__
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app), base_url="http://test"
    ) as client:
        blog = await client.post("/blogs", json=_blog_payload(blog_data))
        blog_id = blog.json()["id"]
        created = await client.post(
            f"/blogs/{blog_id}/posts",
            json={"title": post_data["title"], "body": post_data["body"]}
        )
        post_id = created.json()["id"]
        response = await client.get(f"/posts/{post_id}")

    assert response.status_code == 200


@pytest.mark.asyncio
async def test_get_post_returns_post_data(app: FastAPI):
    blog_data = BlogFactory.stub().__dict__
    post_data = PostFactory.stub().__dict__
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app), base_url="http://test"
    ) as client:
        blog = await client.post("/blogs", json=_blog_payload(blog_data))
        blog_id = blog.json()["id"]
        created = await client.post(
            f"/blogs/{blog_id}/posts",
            json={"title": post_data["title"], "body": post_data["body"]}
        )
        post_id = created.json()["id"]
        response = await client.get(f"/posts/{post_id}")

    body = response.json()
    assert body["id"] == post_id
    assert body["blog_id"] == blog_id
    assert body["title"] == post_data["title"]
    assert body["body"] == post_data["body"]
    assert "created_at" in body
    assert "updated_at" in body


@pytest.mark.asyncio
async def test_get_post_returns_404_for_unknown_id(app: FastAPI):
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get("/posts/nonexistent-post-id")

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_post_appears_in_blog_detail(app: FastAPI):
    blog_data = BlogFactory.stub().__dict__
    post_data = PostFactory.stub().__dict__
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app), base_url="http://test"
    ) as client:
        blog = await client.post("/blogs", json=_blog_payload(blog_data))
        blog_id = blog.json()["id"]
        await client.post(
            f"/blogs/{blog_id}/posts",
            json={"title": post_data["title"], "body": post_data["body"]}
        )
        response = await client.get(f"/blogs/{blog_id}")

    body = response.json()
    assert len(body["posts"]) == 1
    assert body["posts"][0]["title"] == post_data["title"]
