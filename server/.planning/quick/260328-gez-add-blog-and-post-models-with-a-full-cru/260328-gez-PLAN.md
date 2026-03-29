---
phase: quick
plan: 01
type: execute
wave: 1
depends_on: []
files_modified:
  - requirements.txt
  - app/db.py
  - app/models/__init__.py
  - app/models/blog.py
  - app/models/post.py
  - app/schemas/__init__.py
  - app/schemas/blog.py
  - app/schemas/post.py
  - app/controllers/blogs.py
  - app/controllers/posts.py
  - main.py
  - alembic.ini
  - alembic/env.py
  - alembic/script.py.mako
  - alembic/versions/
  - tests/app/controllers/test_blogs.py
  - tests/app/controllers/test_posts.py
  - tests/conftest.py
autonomous: true
requirements: []
must_haves:
  truths:
    - "POST /blogs creates a blog and returns it with an id"
    - "GET /blogs returns a list of all blogs"
    - "GET /blogs/{id} returns a single blog with its posts"
    - "PATCH /blogs/{id} updates blog name and/or description"
    - "POST /blogs/{blog_id}/posts creates a post under a blog"
    - "Alembic migration exists for Blog and Post tables"
  artifacts:
    - path: "app/db.py"
      provides: "Async SQLAlchemy engine, session factory, Base"
    - path: "app/models/blog.py"
      provides: "Blog SQLAlchemy model"
    - path: "app/models/post.py"
      provides: "Post SQLAlchemy model"
    - path: "app/schemas/blog.py"
      provides: "Pydantic v2 request/response schemas for blogs"
    - path: "app/schemas/post.py"
      provides: "Pydantic v2 request/response schemas for posts"
    - path: "app/controllers/blogs.py"
      provides: "Blog CRUD endpoints"
    - path: "app/controllers/posts.py"
      provides: "Post creation endpoint"
  key_links:
    - from: "app/controllers/blogs.py"
      to: "app/db.py"
      via: "get_db dependency injection"
      pattern: "Depends.*get_db"
    - from: "app/controllers/blogs.py"
      to: "app/models/blog.py"
      via: "SQLAlchemy queries"
      pattern: "select.*Blog"
    - from: "main.py"
      to: "app/controllers/blogs.py"
      via: "register(app)"
      pattern: "blogs_controller\\.register"
---

<objective>
Add Blog and Post models with full CRUD API to the FastAPI server.

Purpose: Enable blog content management — the core content feature of bigcattechnologies.com.
Output: Working Blog/Post CRUD endpoints backed by async PostgreSQL, with Alembic migrations and tests.
</objective>

<execution_context>
@$HOME/.claude/get-shit-done/workflows/execute-plan.md
@$HOME/.claude/get-shit-done/templates/summary.md
</execution_context>

<context>
@main.py
@app/controllers/health.py
@tests/app/controllers/test_health.py
@requirements.txt

<interfaces>
<!-- Existing controller registration pattern from health.py -->
From app/controllers/health.py:
```python
from fastapi import FastAPI

def register(app: FastAPI):
    @app.get('/health')
    def health(): return { 'status': 'ok' }
```

From main.py:
```python
app = FastAPI(title='Big Cat Technologies', lifespan=mcp_app.lifespan)
health_controller.register(app)
```

From tests/app/controllers/test_health.py:
```python
# Test pattern: create FastAPI app in fixture, register controller, use httpx.AsyncClient with ASGITransport
@pytest.fixture
def app() -> FastAPI:
    app = FastAPI()
    register(app)
    return app

@pytest.mark.asyncio
async def test_health_returns_200(app: FastAPI):
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get("/health")
    assert response.status_code == 200
```
</interfaces>
</context>

<tasks>

<task type="auto">
  <name>Task 1: Database layer, models, schemas, and Alembic setup</name>
  <files>
    requirements.txt,
    app/db.py,
    app/models/__init__.py,
    app/models/blog.py,
    app/models/post.py,
    app/schemas/__init__.py,
    app/schemas/blog.py,
    app/schemas/post.py,
    alembic.ini,
    alembic/env.py,
    alembic/script.py.mako
  </files>
  <action>
1. **Update requirements.txt** — Add: `sqlalchemy[asyncio]`, `asyncpg`, `alembic`, `greenlet` (needed by SQLAlchemy async).

2. **Create `app/db.py`** — Async SQLAlchemy setup:
   - Read env vars: `DB_HOST`, `DB_NAME`, `DB_USER`, `DB_PASSWORD` using `os.environ.get()` with sensible defaults (host=`/cloudsql/...` or `localhost`, name=`bigcat`, user=`postgres`, password empty).
   - Build connection string: `postgresql+asyncpg://{user}:{password}@/{db_name}?host={db_host}`
   - Create `engine = create_async_engine(DATABASE_URL)`
   - Create `async_session = async_sessionmaker(engine, expire_on_commit=False)`
   - Create `Base = DeclarativeBase` subclass
   - Create `async def get_db()` async generator that yields an `AsyncSession` and closes it (for use as FastAPI `Depends`)

3. **Create `app/models/__init__.py`** — Import Blog and Post so Alembic autogenerate can discover them. Export `Base` from db.py for convenience.

4. **Create `app/models/blog.py`** — SQLAlchemy 2.0 mapped class:
   - `id`: `Mapped[uuid.UUID]` primary key, default `uuid.uuid4`
   - `name`: `Mapped[str]` (max 200)
   - `description`: `Mapped[str]` (Text)
   - `created_at`: `Mapped[datetime]` server_default=`func.now()`
   - `updated_at`: `Mapped[datetime]` server_default=`func.now()`, onupdate=`func.now()`
   - `posts`: `relationship("Post", back_populates="blog", lazy="selectin")`

5. **Create `app/models/post.py`** — SQLAlchemy 2.0 mapped class:
   - `id`: `Mapped[uuid.UUID]` primary key, default `uuid.uuid4`
   - `blog_id`: `Mapped[uuid.UUID]` ForeignKey("blogs.id")
   - `title`: `Mapped[str]` (max 300)
   - `body`: `Mapped[str]` (Text)
   - `created_at`: `Mapped[datetime]` server_default=`func.now()`
   - `updated_at`: `Mapped[datetime]` server_default=`func.now()`, onupdate=`func.now()`
   - `blog`: `relationship("Blog", back_populates="posts")`

6. **Create Pydantic v2 schemas:**

   `app/schemas/blog.py`:
   - `BlogCreate(BaseModel)`: name (str), description (str)
   - `BlogUpdate(BaseModel)`: name (str | None = None), description (str | None = None)
   - `BlogResponse(BaseModel)`: id (UUID), name, description, created_at (datetime). Use `model_config = ConfigDict(from_attributes=True)`.
   - `BlogDetailResponse(BlogResponse)`: posts (list[PostResponse]). Import PostResponse from post schemas.

   `app/schemas/post.py`:
   - `PostCreate(BaseModel)`: title (str), body (str)
   - `PostResponse(BaseModel)`: id (UUID), blog_id (UUID), title, body, created_at (datetime). Use `model_config = ConfigDict(from_attributes=True)`.

   `app/schemas/__init__.py`: empty or re-exports.

   NOTE: To avoid circular imports, define PostResponse in `post.py` first, then import it in `blog.py` for BlogDetailResponse.

7. **Initialize Alembic:**
   - Run `alembic init alembic` to scaffold.
   - Edit `alembic.ini`: set `sqlalchemy.url` to empty (will be overridden in env.py).
   - Edit `alembic/env.py`:
     - Import `asyncio` and `from sqlalchemy.ext.asyncio import async_engine_from_config`.
     - Import `Base` and all models from `app.models` so metadata is populated.
     - Import the `DATABASE_URL` from `app.db` and set `config.set_main_option("sqlalchemy.url", DATABASE_URL)`.
     - Replace `run_migrations_online()` with an async version that uses `async_engine_from_config` and `run_sync`.
     - Keep `run_migrations_offline()` as-is.
   - Do NOT run `alembic revision --autogenerate` yet (no DB available in CI). Just set up the config so the user can run it when connected to a database.
  </action>
  <verify>
    <automated>cd /home/theclaw/Desktop/projects/BigCatTechnologies/server && python -c "from app.models import Base, Blog, Post; from app.schemas.blog import BlogCreate, BlogUpdate, BlogResponse, BlogDetailResponse; from app.schemas.post import PostCreate, PostResponse; print('All imports OK')"</automated>
  </verify>
  <done>
    - app/db.py exports engine, async_session, Base, get_db
    - Blog and Post models importable with correct fields and relationship
    - Pydantic schemas importable for all request/response types
    - Alembic configured for async PostgreSQL (alembic.ini + env.py)
    - requirements.txt includes sqlalchemy[asyncio], asyncpg, alembic
  </done>
</task>

<task type="auto">
  <name>Task 2: Blog and Post controllers wired into main.py</name>
  <files>
    app/controllers/blogs.py,
    app/controllers/posts.py,
    main.py
  </files>
  <action>
1. **Create `app/controllers/blogs.py`** following the existing `register(app)` pattern:

   ```python
   from fastapi import FastAPI, Depends, HTTPException
   from sqlalchemy.ext.asyncio import AsyncSession
   from sqlalchemy import select
   from app.db import get_db
   from app.models.blog import Blog
   from app.schemas.blog import BlogCreate, BlogUpdate, BlogResponse, BlogDetailResponse

   def register(app: FastAPI):

       @app.post('/blogs', response_model=BlogResponse, status_code=201)
       async def create_blog(data: BlogCreate, db: AsyncSession = Depends(get_db)):
           blog = Blog(name=data.name, description=data.description)
           db.add(blog)
           await db.commit()
           await db.refresh(blog)
           return blog

       @app.get('/blogs', response_model=list[BlogResponse])
       async def list_blogs(db: AsyncSession = Depends(get_db)):
           result = await db.execute(select(Blog).order_by(Blog.created_at.desc()))
           return result.scalars().all()

       @app.get('/blogs/{blog_id}', response_model=BlogDetailResponse)
       async def get_blog(blog_id: str, db: AsyncSession = Depends(get_db)):
           result = await db.execute(select(Blog).where(Blog.id == blog_id))
           blog = result.scalar_one_or_none()
           if not blog:
               raise HTTPException(status_code=404, detail="Blog not found")
           return blog

       @app.patch('/blogs/{blog_id}', response_model=BlogResponse)
       async def update_blog(blog_id: str, data: BlogUpdate, db: AsyncSession = Depends(get_db)):
           result = await db.execute(select(Blog).where(Blog.id == blog_id))
           blog = result.scalar_one_or_none()
           if not blog:
               raise HTTPException(status_code=404, detail="Blog not found")
           if data.name is not None:
               blog.name = data.name
           if data.description is not None:
               blog.description = data.description
           await db.commit()
           await db.refresh(blog)
           return blog
   ```

   Use UUID type for blog_id parameter (import from uuid). The `blog_id` path param should be typed as `uuid.UUID` not `str`.

2. **Create `app/controllers/posts.py`** following the same pattern:

   ```python
   def register(app: FastAPI):

       @app.post('/blogs/{blog_id}/posts', response_model=PostResponse, status_code=201)
       async def create_post(blog_id: uuid.UUID, data: PostCreate, db: AsyncSession = Depends(get_db)):
           # Verify blog exists
           result = await db.execute(select(Blog).where(Blog.id == blog_id))
           if not result.scalar_one_or_none():
               raise HTTPException(status_code=404, detail="Blog not found")
           post = Post(blog_id=blog_id, title=data.title, body=data.body)
           db.add(post)
           await db.commit()
           await db.refresh(post)
           return post
   ```

3. **Update `main.py`** — Add imports and register calls:
   - `from app.controllers import blogs as blogs_controller`
   - `from app.controllers import posts as posts_controller`
   - Call `blogs_controller.register(app)` and `posts_controller.register(app)` after `health_controller.register(app)` and BEFORE `app.mount('/', mcp_app)` (mount must be last since it catches all routes).
  </action>
  <verify>
    <automated>cd /home/theclaw/Desktop/projects/BigCatTechnologies/server && python -c "from main import app; routes = [r.path for r in app.routes]; assert '/blogs' in routes; assert '/blogs/{blog_id}' in routes; assert '/blogs/{blog_id}/posts' in routes; print('Routes registered:', routes)"</automated>
  </verify>
  <done>
    - POST /blogs, GET /blogs, GET /blogs/{id}, PATCH /blogs/{id} endpoints exist
    - POST /blogs/{blog_id}/posts endpoint exists
    - All endpoints use async db sessions via Depends(get_db)
    - 404 returned for non-existent blog lookups
    - Controllers follow the existing register(app) pattern
    - main.py registers both controllers before MCP mount
  </done>
</task>

<task type="auto">
  <name>Task 3: Tests for blog and post endpoints</name>
  <files>
    tests/conftest.py,
    tests/app/controllers/test_blogs.py,
    tests/app/controllers/test_posts.py
  </files>
  <action>
Tests must NOT require a real database. Mock the `get_db` dependency using FastAPI's `app.dependency_overrides`.

1. **Create `tests/conftest.py`** with a shared async SQLite in-memory database for tests:

   ```python
   import pytest
   from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
   from app.db import Base, get_db
   from fastapi import FastAPI

   # Use aiosqlite for in-memory test DB (add aiosqlite to requirements.txt)
   TEST_DB_URL = "sqlite+aiosqlite:///:memory:"

   @pytest.fixture
   async def db_session():
       engine = create_async_engine(TEST_DB_URL)
       async with engine.begin() as conn:
           await conn.run_sync(Base.metadata.create_all)
       session_factory = async_sessionmaker(engine, expire_on_commit=False)
       async with session_factory() as session:
           yield session
       async with engine.begin() as conn:
           await conn.run_sync(Base.metadata.drop_all)
       await engine.dispose()
   ```

   Add `aiosqlite` to requirements.txt for the test SQLite async driver.

2. **Create `tests/app/controllers/test_blogs.py`** following the httpx.AsyncClient + ASGITransport pattern from test_health.py:

   ```python
   @pytest.fixture
   def app(db_session) -> FastAPI:
       app = FastAPI()
       app.dependency_overrides[get_db] = lambda: db_session
       blogs_controller.register(app)
       posts_controller.register(app)  # needed for BlogDetailResponse with posts
       return app
   ```

   Test cases:
   - `test_create_blog_returns_201` — POST /blogs with valid data, assert 201 and response has id, name, description, created_at
   - `test_list_blogs_returns_empty` — GET /blogs on fresh db returns []
   - `test_list_blogs_returns_created` — Create a blog, then GET /blogs returns list with 1 item
   - `test_get_blog_returns_404` — GET /blogs/{random_uuid} returns 404
   - `test_get_blog_returns_blog_with_posts` — Create blog + post, GET /blogs/{id} returns blog with posts list
   - `test_update_blog_name` — PATCH /blogs/{id} with new name, assert name changed
   - `test_update_blog_returns_404` — PATCH /blogs/{random_uuid} returns 404

3. **Create `tests/app/controllers/test_posts.py`**:
   - `test_create_post_returns_201` — POST /blogs/{blog_id}/posts with valid data
   - `test_create_post_blog_not_found` — POST /blogs/{random_uuid}/posts returns 404

   All tests use `@pytest.mark.asyncio` and `httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test")`.

   IMPORTANT: The `app.dependency_overrides[get_db]` must be set to an `async def` that yields the session, not a lambda returning it, because `get_db` is an async generator. Use:
   ```python
   async def override_get_db():
       yield db_session
   app.dependency_overrides[get_db] = override_get_db
   ```
  </action>
  <verify>
    <automated>cd /home/theclaw/Desktop/projects/BigCatTechnologies/server && pip install aiosqlite -q && python -m pytest tests/ -x -v 2>&1 | tail -30</automated>
  </verify>
  <done>
    - All blog CRUD tests pass (create, list, get, get-404, update, update-404)
    - All post tests pass (create, create-blog-not-found)
    - Tests use in-memory SQLite, no real PostgreSQL required
    - Existing health tests still pass
    - aiosqlite added to requirements.txt
  </done>
</task>

</tasks>

<verification>
1. All imports work: `python -c "from app.models import Blog, Post; from app.controllers import blogs, posts; print('OK')"`
2. All tests pass: `python -m pytest tests/ -x -v`
3. Routes registered: `python -c "from main import app; print([r.path for r in app.routes])"`
4. Alembic config valid: `python -c "from alembic.config import Config; c = Config('alembic.ini'); print('Alembic OK')"`
</verification>

<success_criteria>
- Blog and Post models with UUID PKs and timestamps exist
- Pydantic v2 schemas for all request/response types
- 5 CRUD endpoints (4 blog + 1 post) registered and functional
- Alembic configured for async PostgreSQL migrations
- All tests pass without a real database
- Existing health endpoint and tests unaffected
</success_criteria>

<output>
After completion, create `.planning/quick/260328-gez-add-blog-and-post-models-with-a-full-cru/260328-gez-SUMMARY.md`
</output>
