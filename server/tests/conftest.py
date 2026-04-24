import pytest
from fastapi import FastAPI
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

from app.auth.dependencies import require_auth0_token
from app.auth.token import SessionToken
from app.db import get_db, Base
from app.controllers.blogs import register as register_blogs
from app.controllers.posts import register as register_posts
from app.controllers.admin.blogs import register as register_admin_blogs
from app.controllers.auth import register as register_auth
from app.controllers.social import register as register_social
from app.models.blog import Blog
from app.models.post import Post
from app.models.user import User
from app.models.social_token import SocialToken
from tests.factories import BlogFactory, PostFactory, UserFactory, SocialTokenFactory

TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest.fixture
async def db_session():
    engine = create_async_engine(TEST_DATABASE_URL, echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    session_factory = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)
    async with session_factory() as session:
        yield session
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest.fixture
def app(db_session: AsyncSession) -> FastAPI:
    test_app = FastAPI()
    register_blogs(test_app)
    register_posts(test_app)

    async def override_get_db():
        yield db_session

    test_app.dependency_overrides[get_db] = override_get_db
    return test_app


@pytest.fixture
def admin_app(db_session: AsyncSession) -> FastAPI:
    test_app = FastAPI()
    register_admin_blogs(test_app)

    async def override_get_db():
        yield db_session

    async def override_require_auth0_token():
        return SessionToken(sub="auth0|test123", permissions=["admin"])

    test_app.dependency_overrides[get_db] = override_get_db
    test_app.dependency_overrides[require_auth0_token] = override_require_auth0_token
    return test_app


async def create_blog(db: AsyncSession, **kwargs) -> Blog:
    """Create and persist a Blog using BlogFactory defaults, with optional overrides."""
    blog = BlogFactory.build(**kwargs)
    db.add(blog)
    await db.commit()
    await db.refresh(blog)
    return blog


async def create_post(db: AsyncSession, blog: Blog = None, **kwargs) -> Post:
    """Create and persist a Post using PostFactory defaults, with optional overrides.

    If no blog is provided, one will be created automatically.
    """
    if blog is None:
        blog = await create_blog(db)
    post = PostFactory.build(blog_id=blog.id, **kwargs)
    db.add(post)
    await db.commit()
    await db.refresh(post)
    return post


@pytest.fixture
def linkedin_app(db_session: AsyncSession) -> FastAPI:
    test_app = FastAPI()
    register_auth(test_app)
    register_social(test_app)

    async def override_get_db():
        yield db_session

    async def override_require_auth0_token():
        return SessionToken(sub="auth0|linkedintest", permissions=[])

    test_app.dependency_overrides[get_db] = override_get_db
    test_app.dependency_overrides[require_auth0_token] = override_require_auth0_token
    return test_app


async def create_user(db: AsyncSession, **kwargs) -> User:
    """Create and persist a User using UserFactory defaults, with optional overrides."""
    user = UserFactory.build(**kwargs)
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


async def create_social_token(db: AsyncSession, user: User = None, **kwargs) -> SocialToken:
    """Create and persist a SocialToken using SocialTokenFactory defaults, with optional overrides."""
    if user is None:
        user = await create_user(db)
    token = SocialTokenFactory.build(user_id=user.id, **kwargs)
    db.add(token)
    await db.commit()
    await db.refresh(token)
    return token
