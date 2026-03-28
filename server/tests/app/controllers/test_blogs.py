import pytest
import httpx
from fastapi import FastAPI
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase

from app.controllers.blogs import register
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
    register(test_app)

    async def override_get_db():
        yield db_session

    test_app.dependency_overrides[get_db] = override_get_db
    return test_app


@pytest.mark.asyncio
async def test_create_blog_returns_201(app: FastAPI):
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.post("/blogs", json={"name": "My Blog", "description": "A test blog"})

    assert response.status_code == 201


@pytest.mark.asyncio
async def test_create_blog_returns_blog_data(app: FastAPI):
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.post("/blogs", json={"name": "My Blog", "description": "A test blog"})

    body = response.json()
    assert body["name"] == "My Blog"
    assert body["description"] == "A test blog"
    assert "id" in body
    assert "created_at" in body
    assert "updated_at" in body


@pytest.mark.asyncio
async def test_list_blogs_returns_200(app: FastAPI):
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get("/blogs")

    assert response.status_code == 200


@pytest.mark.asyncio
async def test_list_blogs_returns_created_blogs(app: FastAPI):
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app), base_url="http://test"
    ) as client:
        await client.post("/blogs", json={"name": "Blog One", "description": ""})
        await client.post("/blogs", json={"name": "Blog Two", "description": ""})
        response = await client.get("/blogs")

    body = response.json()
    assert len(body) == 2
    names = [b["name"] for b in body]
    assert "Blog One" in names
    assert "Blog Two" in names


@pytest.mark.asyncio
async def test_get_blog_returns_200(app: FastAPI):
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app), base_url="http://test"
    ) as client:
        created = await client.post("/blogs", json={"name": "My Blog", "description": ""})
        blog_id = created.json()["id"]
        response = await client.get(f"/blogs/{blog_id}")

    assert response.status_code == 200


@pytest.mark.asyncio
async def test_get_blog_returns_blog_with_posts(app: FastAPI):
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app), base_url="http://test"
    ) as client:
        created = await client.post("/blogs", json={"name": "My Blog", "description": ""})
        blog_id = created.json()["id"]
        response = await client.get(f"/blogs/{blog_id}")

    body = response.json()
    assert body["id"] == blog_id
    assert "posts" in body
    assert isinstance(body["posts"], list)


@pytest.mark.asyncio
async def test_get_blog_returns_404_for_unknown_id(app: FastAPI):
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get("/blogs/nonexistent-id")

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_update_blog_returns_200(app: FastAPI):
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app), base_url="http://test"
    ) as client:
        created = await client.post("/blogs", json={"name": "Old Name", "description": ""})
        blog_id = created.json()["id"]
        response = await client.patch(f"/blogs/{blog_id}", json={"name": "New Name"})

    assert response.status_code == 200


@pytest.mark.asyncio
async def test_update_blog_changes_name(app: FastAPI):
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app), base_url="http://test"
    ) as client:
        created = await client.post("/blogs", json={"name": "Old Name", "description": ""})
        blog_id = created.json()["id"]
        response = await client.patch(f"/blogs/{blog_id}", json={"name": "New Name"})

    assert response.json()["name"] == "New Name"


@pytest.mark.asyncio
async def test_update_blog_returns_404_for_unknown_id(app: FastAPI):
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.patch("/blogs/nonexistent-id", json={"name": "New Name"})

    assert response.status_code == 404
