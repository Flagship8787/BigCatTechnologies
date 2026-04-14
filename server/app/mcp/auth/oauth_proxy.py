import base64
import json
import os
from typing import Any

from dotenv import load_dotenv
from fastmcp.server.auth import OAuthProxy
from fastmcp.server.auth.providers.jwt import JWTVerifier
from key_value.aio.stores.redis import RedisStore
from redis.asyncio import Redis

load_dotenv()

redis_args = {
    'host': os.environ['REDIS_HOST'],
    'port': int(os.environ['REDIS_PORT']),
    'password': os.environ['REDIS_PASSWORD'],
    'ssl': False,
    'decode_responses': True
}

if os.environ['REDIS_USE_SSL'].lower() == 'true':
    redis_args['ssl']=True
    redis_args['ssl_cert_reqs']='required'

redis_client = Redis(**redis_args)
cache_storage = RedisStore(client=redis_client)

token_verifier = JWTVerifier(
    jwks_uri=os.environ['AUTH0_JWKS_URI'],
    issuer=os.environ['AUTH0_ISSUER'],
    audience=os.environ['AUTH0_AUDIENCE']
)


def _decode_jwt_payload(token: str) -> dict:
    """Decode JWT payload without signature verification."""
    parts = token.split('.')
    if len(parts) != 3:
        return {}
    payload = parts[1]
    # Add padding
    payload += '=' * (4 - len(payload) % 4)
    try:
        return json.loads(base64.urlsafe_b64decode(payload))
    except Exception:
        return {}


class Auth0OAuthProxy(OAuthProxy):
    """OAuthProxy subclass that extracts Auth0 claims into the FastMCP JWT.

    Auth0 access tokens are JWTs containing `sub`, `permissions`, `scope`,
    and other user identity claims. By default OAuthProxy._extract_upstream_claims
    returns None, so these claims are lost. This subclass decodes the upstream
    Auth0 access token and returns the relevant claims so they are embedded
    in the FastMCP JWT under the `upstream_claims` key.
    """

    async def _extract_upstream_claims(
        self, idp_tokens: dict[str, Any]
    ) -> dict[str, Any] | None:
        """Extract Auth0 claims from the upstream access token."""
        access_token = idp_tokens.get('access_token')
        if not access_token:
            return None

        payload = _decode_jwt_payload(access_token)
        if not payload:
            return None

        claims: dict[str, Any] = {}

        if sub := payload.get('sub'):
            claims['sub'] = sub
        if permissions := payload.get('permissions'):
            claims['permissions'] = permissions
        if scope := payload.get('scope'):
            claims['scope'] = scope

        return claims or None


auth = Auth0OAuthProxy(
    upstream_authorization_endpoint=os.environ['AUTH0_AUTH_ENDPOINT'],
    upstream_token_endpoint=os.environ['AUTH0_TOKEN_ENDPOINT'],
    upstream_client_id=os.environ['AUTH0_MCP_CLIENT_ID'],
    upstream_client_secret=os.environ['AUTH0_MCP_CLIENT_SECRET'],
    token_verifier=token_verifier,
    base_url=os.environ['API_BASE_URL'],
    redirect_path=os.environ['AUTH0_REDIRECT_PATH'],
    client_storage=cache_storage,
    allowed_client_redirect_uris=["http://localhost", "http://127.0.0.1"],
    extra_authorize_params={"audience": os.environ['AUTH0_AUDIENCE'], "scope": "openid offline_access"},
    extra_token_params={"audience": os.environ['AUTH0_AUDIENCE']},
)
