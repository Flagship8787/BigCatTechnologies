import os
from dotenv import load_dotenv
from fastmcp.server.auth import OAuthProxy
from fastmcp.server.auth.providers.jwt import JWTVerifier
from key_value.aio.stores.redis import RedisStore
from redis.asyncio import Redis

load_dotenv()

redis_args = {
    'host': os.environ['REDIS_HOST'],
    'port': os.environ['REDIS_PORT'],
    'ssl': False,
    'decode_responses': True
}

if os.environ['REDIS_USE_SSL'].lower() == 'true'
    redis_args['ssl']=True
    redis_args['ssl_cert_reqs']='required'

redis_client = Redis(**redis_args)
cache_storage = RedisStore(client=redis_client)

token_verifier = JWTVerifier(
    jwks_uri=os.environ['AUTH0_JWKS_URI'],
    issuer=os.environ['AUTH0_ISSUER'],
    audience=os.environ['AUTH0_AUDIENCE']
)

auth = OAuthProxy(
    upstream_authorization_endpoint=os.environ['AUTH0_AUTH_ENDPOINT'],
    upstream_token_endpoint=os.environ['AUTH0_TOKEN_ENDPOINT'],
    upstream_client_id=os.environ['AUTH0_CLIENT_ID'],
    upstream_client_secret=os.environ['AUTH0_CLIENT_SECRET'],
    token_verifier=token_verifier,
    base_url=os.environ['API_BASE_URL'],
    redirect_path=os.environ['AUTH0_REDIRECT_PATH'],
    cache_storage=cache_storage
)