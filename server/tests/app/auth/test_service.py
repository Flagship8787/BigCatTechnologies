import os
from contextlib import ExitStack
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import HTTPException
from jose import JWTError

from app.auth.service import AuthService
from app.auth.token import SessionToken

VALID_SUB = "auth0|testuser123"

MOCK_JWKS = {
    "keys": [
        {
            "kty": "RSA",
            "kid": "test-key-id",
            "use": "sig",
            "n": "test-n",
            "e": "test-e",
        }
    ]
}

MOCK_PAYLOAD = {
    "sub": VALID_SUB,
    "scope": "openid profile",
    "permissions": [],
    "iss": "https://example.auth0.com/",
    "aud": "https://api.example.com",
    "exp": 9999999999,
    "iat": 1700000000,
}

MOCK_ENV = {
    "AUTH0_JWKS_URI": "https://example.auth0.com/.well-known/jwks.json",
    "AUTH0_ISSUER": "https://example.auth0.com/",
    "AUTH0_AUDIENCE": "https://api.example.com",
}

MOCK_TOKEN = "mock.jwt.token"


@pytest.fixture
def auth_service() -> AuthService:
    """Return a fresh AuthService instance for each test."""
    return AuthService()


def _make_mock_httpx_client(return_json: dict) -> MagicMock:
    """Helper: return a mock httpx AsyncClient context manager yielding a response."""
    mock_response = MagicMock()
    mock_response.json.return_value = return_json
    mock_response.raise_for_status = MagicMock()

    mock_client = AsyncMock()
    mock_client.get = AsyncMock(return_value=mock_response)

    mock_context = MagicMock()
    mock_context.__aenter__ = AsyncMock(return_value=mock_client)
    mock_context.__aexit__ = AsyncMock(return_value=False)

    return mock_context, mock_client


class TestGetJwks:
    """Tests for AuthService.get_jwks()."""

    @pytest.mark.asyncio
    async def test_cache_starts_as_none(self, auth_service: AuthService):
        assert auth_service._jwks_cache is None

    @pytest.mark.asyncio
    async def test_returns_jwks_on_first_call(self, auth_service: AuthService):
        mock_context, _ = _make_mock_httpx_client(MOCK_JWKS)

        with patch.dict(os.environ, MOCK_ENV):
            with patch("app.auth.service.httpx.AsyncClient", return_value=mock_context):
                result = await auth_service.get_jwks()

        assert result == MOCK_JWKS

    @pytest.mark.asyncio
    async def test_cache_is_populated_after_first_call(self, auth_service: AuthService):
        mock_context, _ = _make_mock_httpx_client(MOCK_JWKS)

        with patch.dict(os.environ, MOCK_ENV):
            with patch("app.auth.service.httpx.AsyncClient", return_value=mock_context):
                await auth_service.get_jwks()

        assert auth_service._jwks_cache == MOCK_JWKS

    @pytest.mark.asyncio
    async def test_returns_cached_result_on_second_call_without_http_request(
        self, auth_service: AuthService
    ):
        mock_context, mock_client = _make_mock_httpx_client(MOCK_JWKS)

        with patch.dict(os.environ, MOCK_ENV):
            with patch("app.auth.service.httpx.AsyncClient", return_value=mock_context) as MockClient:
                first_result = await auth_service.get_jwks()
                second_result = await auth_service.get_jwks()

        assert first_result == second_result == MOCK_JWKS
        # HTTP client should only have been entered once (second call uses cache)
        assert MockClient.call_count == 1
        assert mock_client.get.call_count == 1


class TestValidateToken:
    """Tests for AuthService.validate_token()."""

    @pytest.mark.asyncio
    async def test_returns_session_token_with_correct_sub_for_valid_token(
        self, auth_service: AuthService
    ):
        with patch.dict(os.environ, MOCK_ENV):
            with patch.object(auth_service, "get_jwks", new=AsyncMock(return_value=MOCK_JWKS)):
                with patch("app.auth.service.jwt.get_unverified_header", return_value={"kid": "test-key-id"}):
                    with patch("app.auth.service.jwt.decode", return_value=MOCK_PAYLOAD):
                        result = await auth_service.validate_token(MOCK_TOKEN)

        assert isinstance(result, SessionToken)
        assert result.sub == VALID_SUB

    @pytest.mark.asyncio
    async def test_raises_401_with_invalid_token_header_when_get_unverified_header_raises(
        self, auth_service: AuthService
    ):
        with patch.dict(os.environ, MOCK_ENV):
            with patch.object(auth_service, "get_jwks", new=AsyncMock(return_value=MOCK_JWKS)):
                with patch(
                    "app.auth.service.jwt.get_unverified_header",
                    side_effect=JWTError("bad header"),
                ):
                    with pytest.raises(HTTPException) as exc_info:
                        await auth_service.validate_token(MOCK_TOKEN)

        assert exc_info.value.status_code == 401
        assert exc_info.value.detail == "Invalid token header"

    @pytest.mark.asyncio
    async def test_raises_401_with_unable_to_find_key_when_no_matching_kid(
        self, auth_service: AuthService
    ):
        with patch.dict(os.environ, MOCK_ENV):
            with patch.object(auth_service, "get_jwks", new=AsyncMock(return_value={"keys": []})):
                with patch(
                    "app.auth.service.jwt.get_unverified_header",
                    return_value={"kid": "no-such-key"},
                ):
                    with pytest.raises(HTTPException) as exc_info:
                        await auth_service.validate_token(MOCK_TOKEN)

        assert exc_info.value.status_code == 401
        assert exc_info.value.detail == "Unable to find appropriate key"

    @pytest.mark.asyncio
    async def test_raises_401_with_invalid_token_when_jwt_decode_raises(
        self, auth_service: AuthService
    ):
        with patch.dict(os.environ, MOCK_ENV):
            with patch.object(auth_service, "get_jwks", new=AsyncMock(return_value=MOCK_JWKS)):
                with patch("app.auth.service.jwt.get_unverified_header", return_value={"kid": "test-key-id"}):
                    with patch("app.auth.service.jwt.decode", side_effect=JWTError("invalid signature")):
                        with pytest.raises(HTTPException) as exc_info:
                            await auth_service.validate_token(MOCK_TOKEN)

        assert exc_info.value.status_code == 401
        assert exc_info.value.detail == "Invalid token"


class TestGetUserinfo:
    """Tests for AuthService.get_userinfo()."""

    @pytest.mark.asyncio
    async def test_returns_profile_dict_from_userinfo_response(self, auth_service: AuthService):
        mock_profile = {"sub": VALID_SUB, "email": "test@example.com", "name": "Test User"}
        mock_context, _ = _make_mock_httpx_client(mock_profile)

        with patch.dict(os.environ, MOCK_ENV):
            with patch("app.auth.service.httpx.AsyncClient", return_value=mock_context):
                result = await auth_service.get_userinfo(MOCK_TOKEN)

        assert result == mock_profile

    @pytest.mark.asyncio
    async def test_sends_correct_authorization_bearer_header(self, auth_service: AuthService):
        mock_context, mock_client = _make_mock_httpx_client({})

        with patch.dict(os.environ, MOCK_ENV):
            with patch("app.auth.service.httpx.AsyncClient", return_value=mock_context):
                await auth_service.get_userinfo(MOCK_TOKEN)

        call_kwargs = mock_client.get.call_args
        headers = call_kwargs.kwargs.get("headers", {})
        assert headers.get("Authorization") == f"Bearer {MOCK_TOKEN}"

    @pytest.mark.asyncio
    async def test_calls_correct_userinfo_url(self, auth_service: AuthService):
        mock_context, mock_client = _make_mock_httpx_client({})

        with patch.dict(os.environ, MOCK_ENV):
            with patch("app.auth.service.httpx.AsyncClient", return_value=mock_context):
                await auth_service.get_userinfo(MOCK_TOKEN)

        expected_url = f"{MOCK_ENV['AUTH0_ISSUER']}userinfo"
        call_args = mock_client.get.call_args
        assert call_args.args[0] == expected_url
