import pytest
import httpx
from fastapi import FastAPI
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import require_auth0_token
from app.auth.token import SessionToken
from app.db import get_db
from app.controllers.admin.users import register as register_admin_users
from tests.conftest import create_user


def _make_admin_app(db_session: AsyncSession, permissions: list) -> FastAPI:
    test_app = FastAPI()
    register_admin_users(test_app)

    async def override_get_db():
        yield db_session

    async def override_require_auth0_token():
        return SessionToken(sub="auth0|test123", permissions=permissions)

    test_app.dependency_overrides[get_db] = override_get_db
    test_app.dependency_overrides[require_auth0_token] = override_require_auth0_token
    return test_app


@pytest.fixture
def unauthed_admin_app(db_session: AsyncSession) -> FastAPI:
    """Admin app without auth override — used to test 401 responses."""
    test_app = FastAPI()
    register_admin_users(test_app)

    async def override_get_db():
        yield db_session

    test_app.dependency_overrides[get_db] = override_get_db
    return test_app


@pytest.fixture
def users_admin_app(db_session: AsyncSession) -> FastAPI:
    return _make_admin_app(db_session, permissions=["admin"])


@pytest.fixture
def no_scope_users_admin_app(db_session: AsyncSession) -> FastAPI:
    """Admin app with a token that has no recognized permissions."""
    return _make_admin_app(db_session, permissions=[])


@pytest.mark.asyncio
async def test_list_users_returns_200(users_admin_app: FastAPI):
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=users_admin_app), base_url="http://test"
    ) as client:
        response = await client.get("/admin/users")

    assert response.status_code == 200


@pytest.mark.asyncio
async def test_list_users_returns_empty_list_when_no_users(users_admin_app: FastAPI):
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=users_admin_app), base_url="http://test"
    ) as client:
        response = await client.get("/admin/users")

    assert response.json() == []


@pytest.mark.asyncio
async def test_list_users_returns_all_users(users_admin_app: FastAPI, db_session: AsyncSession):
    user_one = await create_user(db_session)
    user_two = await create_user(db_session)

    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=users_admin_app), base_url="http://test"
    ) as client:
        response = await client.get("/admin/users")

    body = response.json()
    assert len(body) == 2
    auth0_ids = [u["auth0_id"] for u in body]
    assert user_one.auth0_id in auth0_ids
    assert user_two.auth0_id in auth0_ids


@pytest.mark.asyncio
async def test_list_users_returns_401_without_auth_token(unauthed_admin_app: FastAPI):
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=unauthed_admin_app), base_url="http://test"
    ) as client:
        response = await client.get("/admin/users")

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_list_users_returns_correct_fields(users_admin_app: FastAPI, db_session: AsyncSession):
    await create_user(db_session)

    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=users_admin_app), base_url="http://test"
    ) as client:
        response = await client.get("/admin/users")

    body = response.json()
    assert len(body) == 1
    user = body[0]
    assert set(user.keys()) == {"id", "auth0_id", "created_at", "updated_at"}


@pytest.mark.asyncio
async def test_list_users_returns_403_without_valid_scope(no_scope_users_admin_app: FastAPI):
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=no_scope_users_admin_app), base_url="http://test"
    ) as client:
        response = await client.get("/admin/users")

    assert response.status_code == 403
