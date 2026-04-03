import pytest

from app.auth.deserializer import Deserializer
from app.auth.token import SessionToken


@pytest.fixture
def token_payload():
    return {
        "sub": "auth0|abc123",
        "scope": "openid profile email",
        "permissions": ["admin", "blogs:admin"],
        "iss": "https://example.auth0.com/",
        "aud": "https://api.example.com",
        "exp": 9999999999,
        "iat": 1700000000,
    }


@pytest.fixture
def minimal_token_payload():
    return {
        "sub": "auth0|xyz789",
    }


class TestDeserializer:
    def test_deserialize_returns_session_token(self, token_payload):
        result = Deserializer(token_payload).deserialize()
        assert isinstance(result, SessionToken)

    def test_deserialize_maps_sub(self, token_payload):
        result = Deserializer(token_payload).deserialize()
        assert result.sub == "auth0|abc123"

    def test_deserialize_maps_scope(self, token_payload):
        result = Deserializer(token_payload).deserialize()
        assert result.scope == "openid profile email"

    def test_deserialize_maps_permissions(self, token_payload):
        result = Deserializer(token_payload).deserialize()
        assert result.permissions == ["admin", "blogs:admin"]

    def test_deserialize_maps_optional_fields(self, token_payload):
        result = Deserializer(token_payload).deserialize()
        assert result.iss == "https://example.auth0.com/"
        assert result.aud == "https://api.example.com"
        assert result.exp == 9999999999
        assert result.iat == 1700000000

    def test_deserialize_minimal_payload_sets_optional_fields_to_none(self, minimal_token_payload):
        result = Deserializer(minimal_token_payload).deserialize()
        assert result.sub == "auth0|xyz789"
        assert result.scope == ""
        assert result.permissions == []
        assert result.iss is None
        assert result.aud is None
        assert result.exp is None
        assert result.iat is None

    def test_deserialize_missing_scope_defaults_to_empty_string(self):
        payload = {"sub": "auth0|abc123"}
        result = Deserializer(payload).deserialize()
        assert result.scope == ""

    def test_deserialize_missing_permissions_defaults_to_empty_list(self):
        payload = {"sub": "auth0|abc123"}
        result = Deserializer(payload).deserialize()
        assert result.permissions == []

    def test_deserialize_raises_on_missing_sub(self):
        payload = {"permissions": ["admin"]}
        with pytest.raises(Exception):
            Deserializer(payload).deserialize()
