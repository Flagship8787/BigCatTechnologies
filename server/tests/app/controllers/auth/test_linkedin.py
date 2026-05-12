import pytest
import httpx
from unittest.mock import AsyncMock, patch, MagicMock
from fastapi import FastAPI
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.token import SessionToken
from app.db import get_db
from app.controllers.auth.linkedin import register as register_linkedin, _auth_service
from tests.conftest import create_user


FAKE_ENV = {
    "LINKEDIN_CLIENT_ID": "test-client-id",
    "LINKEDIN_CLIENT_SECRET": "test-client-secret",
    "LINKEDIN_REDIRECT_URI": "https://api.bigcattechnologies.com/auth/linkedin/callback",
    "LINKEDIN_REDIRECT_SUCCESS_URL": "https://bigcattechnologies.com",
}

VALID_TOKEN = "eyJhbGciOiJSUzI1NiJ9.test.token"
VALID_SESSION_TOKEN = SessionToken(sub="auth0|testuser123")

# Patch target for httpx inside the controller module
_HTTPX_PATCH = "app.controllers.auth.linkedin.httpx.AsyncClient"


def _make_app(db_session: AsyncSession) -> FastAPI:
    test_app = FastAPI()
    register_linkedin(test_app)

    async def override_get_db():
        yield db_session

    test_app.dependency_overrides[get_db] = override_get_db
    return test_app


@pytest.fixture
def linkedin_app(db_session: AsyncSession) -> FastAPI:
    return _make_app(db_session)


def _make_mock_http_client(token_data=None, userinfo_data=None):
    """Return a configured mock AsyncClient context manager."""
    token_resp = MagicMock()
    token_resp.raise_for_status = MagicMock()
    token_resp.json.return_value = token_data or {
        "access_token": "li-access-token",
        "refresh_token": "li-refresh-token",
        "expires_in": 3600,
    }

    userinfo_resp = MagicMock()
    userinfo_resp.raise_for_status = MagicMock()
    userinfo_resp.json.return_value = userinfo_data or {"sub": "linkedin-user-id-123"}

    mock_client = AsyncMock()
    mock_client.post = AsyncMock(return_value=token_resp)
    mock_client.get = AsyncMock(return_value=userinfo_resp)
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=False)
    return mock_client


# ---------------------------------------------------------------------------
# GET /auth/linkedin — initiate
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_linkedin_authorize_redirects_to_linkedin(linkedin_app: FastAPI):
    """Valid bearer token should redirect to LinkedIn auth URL."""
    with patch.object(_auth_service, "validate_token", new=AsyncMock(return_value=VALID_SESSION_TOKEN)), \
         patch.dict("os.environ", FAKE_ENV):
        async with httpx.AsyncClient(
            transport=httpx.ASGITransport(app=linkedin_app), base_url="http://test",
            follow_redirects=False,
        ) as client:
            response = await client.get(
                "/auth/linkedin",
                headers={"Authorization": f"Bearer {VALID_TOKEN}"},
            )

    assert response.status_code in (302, 307)
    location = response.headers["location"]
    assert "linkedin.com/oauth/v2/authorization" in location
    assert "client_id=test-client-id" in location
    assert f"state={VALID_TOKEN}" in location


@pytest.mark.asyncio
async def test_linkedin_authorize_embeds_raw_token_as_state(linkedin_app: FastAPI):
    """State param must equal the raw JWT string."""
    with patch.object(_auth_service, "validate_token", new=AsyncMock(return_value=VALID_SESSION_TOKEN)), \
         patch.dict("os.environ", FAKE_ENV):
        async with httpx.AsyncClient(
            transport=httpx.ASGITransport(app=linkedin_app), base_url="http://test",
            follow_redirects=False,
        ) as client:
            response = await client.get(
                "/auth/linkedin",
                headers={"Authorization": f"Bearer {VALID_TOKEN}"},
            )

    from urllib.parse import urlparse, parse_qs
    parsed = urlparse(response.headers["location"])
    qs = parse_qs(parsed.query)
    assert qs["state"][0] == VALID_TOKEN


@pytest.mark.asyncio
async def test_linkedin_authorize_returns_401_without_token(linkedin_app: FastAPI):
    """Missing Authorization header should yield 401/403."""
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=linkedin_app), base_url="http://test",
        follow_redirects=False,
    ) as client:
        response = await client.get("/auth/linkedin")

    assert response.status_code in (401, 403)


@pytest.mark.asyncio
async def test_linkedin_authorize_returns_401_with_invalid_token(linkedin_app: FastAPI):
    """Invalid JWT should yield 401."""
    from fastapi import HTTPException

    with patch.object(
        _auth_service, "validate_token",
        new=AsyncMock(side_effect=HTTPException(status_code=401, detail="Invalid token")),
    ), patch.dict("os.environ", FAKE_ENV):
        async with httpx.AsyncClient(
            transport=httpx.ASGITransport(app=linkedin_app), base_url="http://test",
            follow_redirects=False,
        ) as client:
            response = await client.get(
                "/auth/linkedin",
                headers={"Authorization": "Bearer bad.token.here"},
            )

    assert response.status_code == 401


# ---------------------------------------------------------------------------
# GET /auth/linkedin/callback
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_callback_creates_social_token_and_redirects_connected(
    linkedin_app: FastAPI, db_session: AsyncSession
):
    """Valid code + state should create SocialToken and redirect with ?linkedin=connected."""
    user = await create_user(db_session, auth0_id="auth0|testuser123")
    mock_http = _make_mock_http_client()

    # Open the test client BEFORE patching so httpx.AsyncClient still resolves to the real class
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=linkedin_app), base_url="http://test",
        follow_redirects=False,
    ) as client:
        with patch.object(_auth_service, "validate_token", new=AsyncMock(return_value=VALID_SESSION_TOKEN)), \
             patch.dict("os.environ", FAKE_ENV), \
             patch(_HTTPX_PATCH, return_value=mock_http):
            response = await client.get(
                "/auth/linkedin/callback",
                params={"code": "auth-code-abc", "state": VALID_TOKEN},
            )

    assert response.status_code in (302, 307)
    assert "linkedin=connected" in response.headers["location"]

    # Verify SocialToken was created
    from sqlalchemy import select
    from app.models.social_token import SocialToken
    result = await db_session.execute(
        select(SocialToken).where(SocialToken.user_id == user.id, SocialToken.provider == "linkedin")
    )
    social_token = result.scalar_one_or_none()
    assert social_token is not None
    assert social_token.access_token == "li-access-token"
    assert social_token.refresh_token == "li-refresh-token"
    assert social_token.provider_user_id == "linkedin-user-id-123"


@pytest.mark.asyncio
async def test_callback_upserts_existing_social_token(
    linkedin_app: FastAPI, db_session: AsyncSession
):
    """Reconnecting an existing linked account should update, not duplicate, the SocialToken."""
    user = await create_user(db_session, auth0_id="auth0|testuser123")

    # Pre-create an existing SocialToken
    from app.models.social_token import SocialToken
    existing = SocialToken(
        user_id=user.id,
        provider="linkedin",
        access_token="old-access-token",
        refresh_token="old-refresh-token",
        provider_user_id="linkedin-user-id-123",
    )
    db_session.add(existing)
    await db_session.commit()

    mock_http = _make_mock_http_client()

    # Open the test client BEFORE patching so httpx.AsyncClient still resolves to the real class
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=linkedin_app), base_url="http://test",
        follow_redirects=False,
    ) as client:
        with patch.object(_auth_service, "validate_token", new=AsyncMock(return_value=VALID_SESSION_TOKEN)), \
             patch.dict("os.environ", FAKE_ENV), \
             patch(_HTTPX_PATCH, return_value=mock_http):
            response = await client.get(
                "/auth/linkedin/callback",
                params={"code": "auth-code-abc", "state": VALID_TOKEN},
            )

    assert response.status_code in (302, 307)
    assert "linkedin=connected" in response.headers["location"]

    # Only one SocialToken should exist, with updated values
    from sqlalchemy import select
    result = await db_session.execute(
        select(SocialToken).where(SocialToken.user_id == user.id, SocialToken.provider == "linkedin")
    )
    tokens = result.scalars().all()
    assert len(tokens) == 1
    assert tokens[0].access_token == "li-access-token"


@pytest.mark.asyncio
async def test_callback_redirects_error_with_invalid_state_jwt(
    linkedin_app: FastAPI, db_session: AsyncSession
):
    """Invalid state JWT should redirect with ?linkedin=error."""
    from fastapi import HTTPException

    with patch.object(
        _auth_service, "validate_token",
        new=AsyncMock(side_effect=HTTPException(status_code=401, detail="Invalid token")),
    ), patch.dict("os.environ", FAKE_ENV):
        async with httpx.AsyncClient(
            transport=httpx.ASGITransport(app=linkedin_app), base_url="http://test",
            follow_redirects=False,
        ) as client:
            response = await client.get(
                "/auth/linkedin/callback",
                params={"code": "auth-code-abc", "state": "bad.jwt.token"},
            )

    assert response.status_code in (302, 307)
    assert "linkedin=error" in response.headers["location"]


@pytest.mark.asyncio
async def test_callback_redirects_error_when_user_not_in_db(
    linkedin_app: FastAPI, db_session: AsyncSession
):
    """Valid JWT but user not in DB should redirect with ?linkedin=error."""
    # Don't create any user — DB is empty

    with patch.object(_auth_service, "validate_token", new=AsyncMock(return_value=VALID_SESSION_TOKEN)), \
         patch.dict("os.environ", FAKE_ENV):
        async with httpx.AsyncClient(
            transport=httpx.ASGITransport(app=linkedin_app), base_url="http://test",
            follow_redirects=False,
        ) as client:
            response = await client.get(
                "/auth/linkedin/callback",
                params={"code": "auth-code-abc", "state": VALID_TOKEN},
            )

    assert response.status_code in (302, 307)
    assert "linkedin=error" in response.headers["location"]
