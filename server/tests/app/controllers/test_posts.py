import pytest
import httpx
from fastapi import FastAPI
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

from app.controllers.blogs import register as register_blogs
from app.controllers.posts import register as register_posts
from app.db import get_db, Base


# In-memory SQLite for tests
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest.fixture
async def db_session():
    engine = create_async_engine(TEST_DATABASE_URL, echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    session_factory = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)
    async with session_factory() as session:
        yield session
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest.fixture
def app(db_session: AsyncSession) -> FastAPI:
    test_app = FastAPI()
    register_blogs(test_app)
    register_posts(test_app)

    async def override_get_db():
        yield db_session

    test_app.dependency_overrides[get_db] = override_get_db
    return test_app


@pytest.mark.asyncio
async def test_create_post_returns_201(app: FastAPI):
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app), base_url="http://test"
    ) as client:
        blog = await client.post("/blogs", json={"name": "My Blog", "description": ""})
        blog_id = blog.json()["id"]
        response = await client.post(
            f"/blogs/{blog_id}/posts",
            json={"title": "First Post", "body": "Hello world"}
        )

    assert response.status_code == 201


@pytest.mark.asyncio
async def test_create_post_returns_post_data(app: FastAPI):
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app), base_url="http://test"
    ) as client:
        blog = await client.post("/blogs", json={"name": "My Blog", "description": ""})
        blog_id = blog.json()["id"]
        response = await client.post(
            f"/blogs/{blog_id}/posts",
            json={"title": "First Post", "body": "Hello world"}
        )

    body = response.json()
    assert body["title"] == "First Post"
    assert body["body"] == "Hello world"
    assert body["blog_id"] == blog_id
    assert "id" in body
    assert "created_at" in body
    assert "updated_at" in body


@pytest.mark.asyncio
async def test_create_post_returns_404_for_unknown_blog(app: FastAPI):
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.post(
            "/blogs/nonexistent-id/posts",
            json={"title": "First Post", "body": "Hello world"}
        )

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_post_appears_in_blog_detail(app: FastAPI):
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app), base_url="http://test"
    ) as client:
        blog = await client.post("/blogs", json={"name": "My Blog", "description": ""})
        blog_id = blog.json()["id"]
        await client.post(
            f"/blogs/{blog_id}/posts",
            json={"title": "First Post", "body": "Hello world"}
        )
        response = await client.get(f"/blogs/{blog_id}")

    body = response.json()
    assert len(body["posts"]) == 1
    assert body["posts"][0]["title"] == "First Post"
