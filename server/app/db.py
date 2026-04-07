import os
from urllib.parse import quote_plus
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase


DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = int(os.getenv("DB_PORT", "5432"))
DB_NAME = os.getenv("DB_NAME", "bigcat")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")

# asyncpg requires Unix socket paths to be passed via connect_args, not in the URL.
# Password is URL-encoded to handle special characters safely.
# DB_PORT is ignored by asyncpg when DB_HOST is a Unix socket path.
DATABASE_URL = f"postgresql+asyncpg://{quote_plus(DB_USER)}:{quote_plus(DB_PASSWORD)}@/{DB_NAME}"
CONNECT_ARGS = {"host": DB_HOST, "port": DB_PORT}

engine = create_async_engine(DATABASE_URL, connect_args=CONNECT_ARGS, echo=False)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


class Base(DeclarativeBase):
    pass


async def get_db() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        yield session
