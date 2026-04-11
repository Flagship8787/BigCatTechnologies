from unittest.mock import MagicMock

from fastmcp.server.auth import AuthContext
from fastmcp.server.auth.providers.jwt import AccessToken

from app.mcp.posts.permissions import post_auth, POSTS_CREATE


def _make_ctx(permissions: list | None) -> AuthContext:
    """Build a minimal AuthContext with the given permissions claim."""
    component = MagicMock()
    if permissions is None:
        return AuthContext(token=None, component=component)
    token = AccessToken(
        token="fake.jwt.token",
        client_id="test-client",
        scopes=[],
        claims={"permissions": permissions, "sub": "test-user", "scope": ""},
    )
    return AuthContext(token=token, component=component)


class TestPostAuth:

    def test_returns_true_when_required_permission_present(self):
        check = post_auth(POSTS_CREATE)
        ctx = _make_ctx([POSTS_CREATE])
        assert check(ctx) is True

    def test_returns_false_when_required_permission_absent(self):
        check = post_auth(POSTS_CREATE)
        ctx = _make_ctx(["other:permission"])
        assert check(ctx) is False

    def test_returns_false_when_permissions_empty(self):
        check = post_auth(POSTS_CREATE)
        ctx = _make_ctx([])
        assert check(ctx) is False

    def test_returns_false_when_token_is_none(self):
        check = post_auth(POSTS_CREATE)
        ctx = _make_ctx(None)
        assert check(ctx) is False

    def test_returns_false_when_permissions_claim_missing(self):
        check = post_auth(POSTS_CREATE)
        component = MagicMock()
        token = AccessToken(
            token="fake.jwt.token",
            client_id="test-client",
            scopes=[],
            claims={"sub": "test-user", "scope": ""},  # no permissions key
        )
        ctx = AuthContext(token=token, component=component)
        assert check(ctx) is False

    def test_returns_true_when_any_permission_matches(self):
        # post_auth uses OR logic (any match via has_permission)
        check = post_auth("admin", POSTS_CREATE)
        ctx_both = _make_ctx(["admin", POSTS_CREATE])
        ctx_one = _make_ctx(["admin"])
        assert check(ctx_both) is True
        assert check(ctx_one) is True  # OR logic: one match is enough

    def test_returns_true_when_token_has_extra_permissions(self):
        check = post_auth(POSTS_CREATE)
        ctx = _make_ctx([POSTS_CREATE, "some:other", "admin"])
        assert check(ctx) is True


class TestPostsCreateConstant:

    def test_posts_create_value(self):
        assert POSTS_CREATE == "posts:create"
