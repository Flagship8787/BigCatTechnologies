from unittest.mock import AsyncMock, MagicMock, patch

import pytest
import httpx
from fastapi import FastAPI
from sqlalchemy.ext.asyncio import AsyncSession

from tests.conftest import create_user


AUTH0_SUB = "auth0|linkedintest"
FAKE_LINKEDIN_URL = "https://www.linkedin.com/oauth/v2/authorization?state=fake"
FAKE_USER_ID = "user-id-abc"


@pytest.mark.asyncio
async def test_linkedin_connect_redirects_to_linkedin(linkedin_app: FastAPI, db_session: AsyncSession):
    mock_user = MagicMock()
    mock_user.id = FAKE_USER_ID

    with (
        patch("app.services.linkedin.upsert_user", new=AsyncMock(return_value=mock_user)),
        patch("app.services.linkedin.build_linkedin_auth_url", return_value=FAKE_LINKEDIN_URL),
    ):
        async with httpx.AsyncClient(
            transport=httpx.ASGITransport(app=linkedin_app), base_url="http://test"
        ) as client:
            response = await client.get("/auth/linkedin", follow_redirects=False)

    assert response.status_code == 307
    assert response.headers["location"] == FAKE_LINKEDIN_URL


@pytest.mark.asyncio
async def test_linkedin_connect_upserts_user_with_auth0_sub(linkedin_app: FastAPI, db_session: AsyncSession):
    mock_user = MagicMock()
    mock_user.id = FAKE_USER_ID

    with (
        patch("app.services.linkedin.upsert_user", new=AsyncMock(return_value=mock_user)) as mock_upsert,
        patch("app.services.linkedin.build_linkedin_auth_url", return_value=FAKE_LINKEDIN_URL),
    ):
        async with httpx.AsyncClient(
            transport=httpx.ASGITransport(app=linkedin_app), base_url="http://test"
        ) as client:
            await client.get("/auth/linkedin", follow_redirects=False)

    mock_upsert.assert_called_once()
    call_kwargs = mock_upsert.call_args
    assert call_kwargs.kwargs["auth0_id"] == AUTH0_SUB


@pytest.mark.asyncio
async def test_linkedin_callback_returns_success(linkedin_app: FastAPI, db_session: AsyncSession):
    with patch("app.services.linkedin.exchange_code_for_token", new=AsyncMock(return_value=MagicMock())):
        async with httpx.AsyncClient(
            transport=httpx.ASGITransport(app=linkedin_app), base_url="http://test"
        ) as client:
            response = await client.get(
                "/auth/linkedin/callback",
                params={"code": "auth_code_123", "state": FAKE_USER_ID},
            )

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"


@pytest.mark.asyncio
async def test_linkedin_callback_passes_code_and_state(linkedin_app: FastAPI, db_session: AsyncSession):
    with patch("app.services.linkedin.exchange_code_for_token", new=AsyncMock(return_value=MagicMock())) as mock_exchange:
        async with httpx.AsyncClient(
            transport=httpx.ASGITransport(app=linkedin_app), base_url="http://test"
        ) as client:
            await client.get(
                "/auth/linkedin/callback",
                params={"code": "auth_code_123", "state": FAKE_USER_ID},
            )

    mock_exchange.assert_called_once()
    call_kwargs = mock_exchange.call_args.kwargs
    assert call_kwargs["code"] == "auth_code_123"
    assert call_kwargs["user_id"] == FAKE_USER_ID


@pytest.mark.asyncio
async def test_linkedin_callback_returns_400_on_error(linkedin_app: FastAPI, db_session: AsyncSession):
    with patch(
        "app.services.linkedin.exchange_code_for_token",
        new=AsyncMock(side_effect=Exception("invalid code")),
    ):
        async with httpx.AsyncClient(
            transport=httpx.ASGITransport(app=linkedin_app), base_url="http://test"
        ) as client:
            response = await client.get(
                "/auth/linkedin/callback",
                params={"code": "bad_code", "state": FAKE_USER_ID},
            )

    assert response.status_code == 400
