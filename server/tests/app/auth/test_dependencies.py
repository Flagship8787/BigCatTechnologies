import os
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import HTTPException
from fastapi.security import HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import require_auth0_token
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


def make_credentials(token: str = "mock.jwt.token") -> HTTPAuthorizationCredentials:
    return HTTPAuthorizationCredentials(scheme="Bearer", credentials=token)


@pytest.fixture(autouse=True)
def reset_jwks_cache():
    """Reset the JWKS cache between tests to avoid cross-test pollution."""
    import app.auth.dependencies as deps
    deps._jwks_cache = None
    yield
    deps._jwks_cache = None


class TestRequireAuth0TokenCallsFindOrCreateUser:
    """Tests that require_auth0_token calls FindOrCreateUserOperation with the correct args."""

    @pytest.mark.asyncio
    async def test_calls_find_or_create_with_sub_from_token(self, db_session: AsyncSession):
        with (
            patch.dict(os.environ, MOCK_ENV),
            patch("app.auth.dependencies._get_jwks", new=AsyncMock(return_value=MOCK_JWKS)),
            patch("app.auth.dependencies.jwt.get_unverified_header", return_value={"kid": "test-key-id"}),
            patch("app.auth.dependencies.jwt.decode", return_value=MOCK_PAYLOAD),
            patch("app.auth.dependencies.FindOrCreateUserOperation") as MockOperation,
        ):
            mock_instance = MagicMock()
            mock_instance.perform_in = AsyncMock()
            MockOperation.return_value = mock_instance

            await require_auth0_token(
                credentials=make_credentials(),
                db=db_session,
            )

            MockOperation.assert_called_once()
            mock_instance.perform_in.assert_awaited_once_with(db_session, auth0_id=VALID_SUB)

    @pytest.mark.asyncio
    async def test_passes_db_session_to_find_or_create(self, db_session: AsyncSession):
        with (
            patch.dict(os.environ, MOCK_ENV),
            patch("app.auth.dependencies._get_jwks", new=AsyncMock(return_value=MOCK_JWKS)),
            patch("app.auth.dependencies.jwt.get_unverified_header", return_value={"kid": "test-key-id"}),
            patch("app.auth.dependencies.jwt.decode", return_value=MOCK_PAYLOAD),
            patch("app.auth.dependencies.FindOrCreateUserOperation") as MockOperation,
        ):
            mock_instance = MagicMock()
            mock_instance.perform_in = AsyncMock()
            MockOperation.return_value = mock_instance

            await require_auth0_token(
                credentials=make_credentials(),
                db=db_session,
            )

            call_kwargs = mock_instance.perform_in.call_args
            assert call_kwargs.args[0] is db_session

    @pytest.mark.asyncio
    async def test_passes_auth0_id_matching_token_sub(self, db_session: AsyncSession):
        custom_sub = "auth0|differentuser999"
        payload = {**MOCK_PAYLOAD, "sub": custom_sub}

        with (
            patch.dict(os.environ, MOCK_ENV),
            patch("app.auth.dependencies._get_jwks", new=AsyncMock(return_value=MOCK_JWKS)),
            patch("app.auth.dependencies.jwt.get_unverified_header", return_value={"kid": "test-key-id"}),
            patch("app.auth.dependencies.jwt.decode", return_value=payload),
            patch("app.auth.dependencies.FindOrCreateUserOperation") as MockOperation,
        ):
            mock_instance = MagicMock()
            mock_instance.perform_in = AsyncMock()
            MockOperation.return_value = mock_instance

            await require_auth0_token(
                credentials=make_credentials(),
                db=db_session,
            )

            mock_instance.perform_in.assert_awaited_once_with(db_session, auth0_id=custom_sub)

    @pytest.mark.asyncio
    async def test_returns_session_token_after_find_or_create(self, db_session: AsyncSession):
        with (
            patch.dict(os.environ, MOCK_ENV),
            patch("app.auth.dependencies._get_jwks", new=AsyncMock(return_value=MOCK_JWKS)),
            patch("app.auth.dependencies.jwt.get_unverified_header", return_value={"kid": "test-key-id"}),
            patch("app.auth.dependencies.jwt.decode", return_value=MOCK_PAYLOAD),
            patch("app.auth.dependencies.FindOrCreateUserOperation") as MockOperation,
        ):
            mock_instance = MagicMock()
            mock_instance.perform_in = AsyncMock()
            MockOperation.return_value = mock_instance

            result = await require_auth0_token(
                credentials=make_credentials(),
                db=db_session,
            )

            assert isinstance(result, SessionToken)
            assert result.sub == VALID_SUB


class TestRequireAuth0TokenDoesNotCallFindOrCreateOnError:
    """Tests that FindOrCreateUserOperation is NOT called when auth fails."""

    @pytest.mark.asyncio
    async def test_does_not_call_find_or_create_on_invalid_token_header(self, db_session: AsyncSession):
        from jose import JWTError

        with (
            patch.dict(os.environ, MOCK_ENV),
            patch("app.auth.dependencies._get_jwks", new=AsyncMock(return_value=MOCK_JWKS)),
            patch("app.auth.dependencies.jwt.get_unverified_header", side_effect=JWTError("bad header")),
            patch("app.auth.dependencies.FindOrCreateUserOperation") as MockOperation,
        ):
            mock_instance = MagicMock()
            mock_instance.perform_in = AsyncMock()
            MockOperation.return_value = mock_instance

            with pytest.raises(HTTPException) as exc_info:
                await require_auth0_token(
                    credentials=make_credentials("bad.token"),
                    db=db_session,
                )

            assert exc_info.value.status_code == 401
            mock_instance.perform_in.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_does_not_call_find_or_create_when_key_not_found(self, db_session: AsyncSession):
        with (
            patch.dict(os.environ, MOCK_ENV),
            patch("app.auth.dependencies._get_jwks", new=AsyncMock(return_value={"keys": []})),
            patch("app.auth.dependencies.jwt.get_unverified_header", return_value={"kid": "no-such-key"}),
            patch("app.auth.dependencies.FindOrCreateUserOperation") as MockOperation,
        ):
            mock_instance = MagicMock()
            mock_instance.perform_in = AsyncMock()
            MockOperation.return_value = mock_instance

            with pytest.raises(HTTPException) as exc_info:
                await require_auth0_token(
                    credentials=make_credentials(),
                    db=db_session,
                )

            assert exc_info.value.status_code == 401
            mock_instance.perform_in.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_does_not_call_find_or_create_on_invalid_jwt(self, db_session: AsyncSession):
        from jose import JWTError

        with (
            patch.dict(os.environ, MOCK_ENV),
            patch("app.auth.dependencies._get_jwks", new=AsyncMock(return_value=MOCK_JWKS)),
            patch("app.auth.dependencies.jwt.get_unverified_header", return_value={"kid": "test-key-id"}),
            patch("app.auth.dependencies.jwt.decode", side_effect=JWTError("invalid")),
            patch("app.auth.dependencies.FindOrCreateUserOperation") as MockOperation,
        ):
            mock_instance = MagicMock()
            mock_instance.perform_in = AsyncMock()
            MockOperation.return_value = mock_instance

            with pytest.raises(HTTPException) as exc_info:
                await require_auth0_token(
                    credentials=make_credentials(),
                    db=db_session,
                )

            assert exc_info.value.status_code == 401
            mock_instance.perform_in.assert_not_awaited()
