from unittest.mock import AsyncMock, patch

import pytest
import httpx
from fastapi import FastAPI
from sqlalchemy.ext.asyncio import AsyncSession


AUTH0_SUB = "auth0|linkedintest"
FAKE_POST_URN = "urn:li:ugcPost:123456789"


@pytest.mark.asyncio
async def test_post_to_linkedin_returns_post_urn(linkedin_app: FastAPI, db_session: AsyncSession):
    with patch("app.services.linkedin.post_to_linkedin", new=AsyncMock(return_value=FAKE_POST_URN)):
        async with httpx.AsyncClient(
            transport=httpx.ASGITransport(app=linkedin_app), base_url="http://test"
        ) as client:
            response = await client.post(
                "/social/linkedin/post",
                json={"text": "Hello LinkedIn!"},
            )

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["post_urn"] == FAKE_POST_URN


@pytest.mark.asyncio
async def test_post_to_linkedin_passes_auth0_id_and_text(linkedin_app: FastAPI, db_session: AsyncSession):
    with patch("app.services.linkedin.post_to_linkedin", new=AsyncMock(return_value=FAKE_POST_URN)) as mock_post:
        async with httpx.AsyncClient(
            transport=httpx.ASGITransport(app=linkedin_app), base_url="http://test"
        ) as client:
            await client.post(
                "/social/linkedin/post",
                json={"text": "Hello LinkedIn!"},
            )

    mock_post.assert_called_once()
    call_kwargs = mock_post.call_args.kwargs
    assert call_kwargs["auth0_id"] == AUTH0_SUB
    assert call_kwargs["text"] == "Hello LinkedIn!"


@pytest.mark.asyncio
async def test_post_to_linkedin_returns_400_when_not_connected(linkedin_app: FastAPI, db_session: AsyncSession):
    with patch(
        "app.services.linkedin.post_to_linkedin",
        new=AsyncMock(side_effect=ValueError("No LinkedIn token found for user. Connect LinkedIn first.")),
    ):
        async with httpx.AsyncClient(
            transport=httpx.ASGITransport(app=linkedin_app), base_url="http://test"
        ) as client:
            response = await client.post(
                "/social/linkedin/post",
                json={"text": "Hello LinkedIn!"},
            )

    assert response.status_code == 400


@pytest.mark.asyncio
async def test_post_to_linkedin_returns_502_on_linkedin_api_error(linkedin_app: FastAPI, db_session: AsyncSession):
    with patch(
        "app.services.linkedin.post_to_linkedin",
        new=AsyncMock(side_effect=Exception("LinkedIn API unavailable")),
    ):
        async with httpx.AsyncClient(
            transport=httpx.ASGITransport(app=linkedin_app), base_url="http://test"
        ) as client:
            response = await client.post(
                "/social/linkedin/post",
                json={"text": "Hello LinkedIn!"},
            )

    assert response.status_code == 502
