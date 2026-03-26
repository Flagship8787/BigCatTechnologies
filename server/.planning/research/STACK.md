# Stack Research

**Domain:** Python FastAPI backend with MCP interface, Auth0 SSO, PostgreSQL-backed blog
**Researched:** 2026-03-25
**Confidence:** MEDIUM (all external verification tools denied in this session — versions flagged for manual confirmation before use)

> NOTE ON VERSIONS: WebSearch, WebFetch, and Bash were all denied during this research session. All version numbers below come from training data (knowledge cutoff August 2025). Before installing anything, verify current versions on PyPI: https://pypi.org/project/[package-name]/

---

## Recommended Stack

### Core Technologies

| Technology | Version | Purpose | Why Recommended |
|------------|---------|---------|-----------------|
| Python | 3.12.x | Runtime | 3.12 is the stable LTS-class release as of mid-2025; 3.13 is new and some libraries lag behind. Use 3.12 for maximum ecosystem compatibility. |
| FastAPI | 0.115.x | HTTP API framework | The dominant async Python web framework. Native Pydantic v2 support, OpenAPI auto-generation, dependency injection. Tiangolo maintains it actively. |
| Uvicorn | 0.30.x | ASGI server | Standard production ASGI server for FastAPI. Use with `--workers` behind nginx or via Gunicorn with uvicorn worker class. |
| FastMCP | 2.x | MCP server layer | The canonical Python MCP SDK. v2 introduced a `mount()` pattern that mounts a FastMCP server directly onto a FastAPI app's ASGI stack, sharing the same process. This is the correct integration pattern. |
| PostgreSQL | 16.x | Primary database | The only correct choice for a production blog/portfolio backend. Reliable ACID guarantees, JSON column support for flexible project metadata, and strong async driver support. SQLite is fine locally but not for VPS production with concurrent writes. |
| SQLAlchemy | 2.x (async) | ORM + query layer | SQLAlchemy 2.0+ has a full async API (`AsyncSession`, `async_sessionmaker`). The widest ecosystem support, Alembic integration, and type-annotated mapped classes (via `DeclarativeBase`). Use the async variant (`sqlalchemy[asyncio]` + `asyncpg`). |
| Alembic | 1.13.x | Database migrations | The standard migration tool for SQLAlchemy. No alternative is necessary — it integrates directly, supports autogenerate from models, and handles schema evolution cleanly. |
| asyncpg | 0.29.x | PostgreSQL async driver | The fastest async PostgreSQL driver for Python. Used as the SQLAlchemy async dialect (`postgresql+asyncpg://`). Do not use psycopg2 for async workloads. |
| Pydantic | 2.x | Data validation and serialization | FastAPI depends on Pydantic v2. Use it for request/response schemas, settings management (`pydantic-settings`), and model validation. v2 is 5-10x faster than v1. |
| pydantic-settings | 2.x | Configuration management | Successor to `BaseSettings` extracted from Pydantic core. Reads from `.env` files and environment variables with full type validation. The standard way to manage FastAPI app configuration. |

### Auth Layer

| Technology | Version | Purpose | Why Recommended |
|------------|---------|---------|-----------------|
| python-jose | 3.3.x | JWT validation | Validates Auth0-issued JWTs. Provides JWKS fetching and RS256 verification. Used in the Auth0 FastAPI quickstart pattern. |
| httpx | 0.27.x | Async HTTP client | Used by the auth layer to fetch Auth0's JWKS endpoint asynchronously. Also useful for testing FastAPI apps. Not requests — requests is sync-only. |
| authlib | 1.3.x | OAuth2 / OIDC | Alternative to python-jose if you need full OIDC flow support. For a simple JWT-validation-only pattern (bearer token on protected routes), python-jose is sufficient and simpler. Prefer authlib if you need the full authorization code flow server-side. |

### Supporting Libraries

| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| python-multipart | 0.0.9 | Form and file upload parsing | Required by FastAPI for any form data or file upload endpoints. Install even if not immediately needed — FastAPI will warn without it. |
| slowapi | 0.1.9 | Rate limiting | Wraps Limits/Redis for per-route rate limiting in FastAPI. Use on public read endpoints to prevent scraping abuse. |
| structlog | 24.x | Structured logging | JSON-structured logs are essential for VPS/container deployments. structlog integrates with Python's logging module and supports async contexts cleanly. |
| pytest | 8.x | Test framework | Standard. |
| pytest-asyncio | 0.23.x | Async test support | Required for testing async FastAPI routes and SQLAlchemy async sessions. Set `asyncio_mode = "auto"` in pytest config. |
| httpx | 0.27.x | Test client | FastAPI's `TestClient` is sync (via requests); use `httpx.AsyncClient` with `ASGITransport` for async integration tests. |

### Development Tools

| Tool | Purpose | Notes |
|------|---------|-------|
| uv | Package manager and virtual env | Dramatically faster than pip/poetry. Use `uv sync` for reproducible installs. Lock file is `uv.lock`. Becoming the de facto standard in 2025. |
| ruff | Linting and formatting | Replaces flake8, isort, and black in a single tool. Extremely fast. Configure in `pyproject.toml`. |
| mypy | Static type checking | FastAPI and Pydantic v2 both have excellent type stubs. Run in CI. |
| Docker | Containerization | Use a multi-stage Dockerfile: build stage with uv, runtime stage with slim Python image. The VPS deployment target makes Docker the right choice over bare-metal Python. |
| docker-compose | Local dev environment | Spin up PostgreSQL locally alongside the app. Use a `compose.yaml` (v2 filename convention) with a `db` service for local dev. |

---

## Integration Pattern: FastMCP + FastAPI

This is the most important architectural decision in the stack. FastMCP v2 provides a `mount()` method that attaches the MCP server directly to the FastAPI app as a sub-application. This means:

- Single ASGI process serves both HTTP API routes and MCP protocol routes
- No separate process or port for MCP
- Shared dependency injection context (auth, DB session) is possible
- MCP endpoints live at a configurable path prefix (e.g., `/mcp`)

**Pattern (HIGH confidence from FastMCP v2 docs as of Aug 2025):**

```python
from fastapi import FastAPI
from fastmcp import FastMCP

app = FastAPI()
mcp = FastMCP("BigCatTechLab")

# Define MCP tools/resources on mcp instance
@mcp.tool()
async def get_blog_posts() -> list[dict]:
    ...

# Mount MCP onto FastAPI
app.mount("/mcp", mcp.get_asgi_app())
```

The MCP server is accessible via HTTP at `/mcp` using the MCP protocol (SSE or streamable HTTP transport). AI agents (Claude Desktop, Cursor) connect to `https://bigcattechlab.com/mcp`.

**Auth on MCP routes:** FastMCP v2 supports adding middleware/dependencies to the mounted sub-app, but it is less ergonomic than FastAPI's native dependency injection. For the owner-only admin pattern, the simplest approach is to add bearer token validation as ASGI middleware on the `/mcp` mount, rather than trying to use FastAPI's `Depends()` system within MCP tool definitions. Verify current FastMCP docs for the recommended pattern — this area was evolving rapidly.

---

## Installation

```bash
# Create project with uv
uv init bigcattechlab-server
cd bigcattechlab-server

# Core runtime
uv add fastapi uvicorn[standard] fastmcp

# Database
uv add sqlalchemy[asyncio] asyncpg alembic

# Auth
uv add python-jose[cryptography] pydantic-settings httpx

# Utilities
uv add python-multipart structlog slowapi

# Dev dependencies
uv add --dev pytest pytest-asyncio ruff mypy
```

---

## Alternatives Considered

| Recommended | Alternative | When to Use Alternative |
|-------------|-------------|-------------------------|
| PostgreSQL | SQLite | Local development only, or a truly single-user tool with no concurrent writes. Not for VPS production. |
| SQLAlchemy 2 async | Tortoise ORM | If you strongly prefer a Django-style ActiveRecord ORM. Tortoise has FastAPI integration but smaller ecosystem, fewer migration tools, and less community support than SQLAlchemy+Alembic. |
| SQLAlchemy 2 async | SQLModel | SQLModel is a Tiangolo project combining SQLAlchemy + Pydantic, but as of 2025 it still uses SQLAlchemy 1.x patterns under the hood in some areas and the async story is less polished. Avoid for new projects until SQLModel v2 stabilizes fully. |
| python-jose | PyJWT | PyJWT is simpler but requires more manual JWKS handling. python-jose wraps JWKS fetching more cleanly. Acceptable alternative if python-jose maintenance becomes a concern. |
| uv | poetry | Poetry is fine but slower. uv is significantly faster and is becoming the community default in 2025. Use poetry only if team familiarity requires it. |
| uvicorn | hypercorn | Hypercorn supports HTTP/2 and HTTP/3, but uvicorn is better tested with FastAPI and has more community examples. Only switch to hypercorn if HTTP/2 is a hard requirement. |

---

## What NOT to Use

| Avoid | Why | Use Instead |
|-------|-----|-------------|
| Flask | Sync-first, no native async, no built-in OpenAPI. Wrong tool for this domain. | FastAPI |
| Django REST Framework | Heavy, opinionated, sync-first. Carries Django's ORM baggage. Massive overkill for a single-owner API. | FastAPI |
| Tortoise ORM | Smaller ecosystem, less mature migrations, ActiveRecord pattern fights with FastAPI's dependency injection pattern. | SQLAlchemy 2 async |
| SQLModel (current) | Uses SQLAlchemy 1.x internals in async contexts as of mid-2025; the v2 rewrite was in progress but not stable. Re-evaluate after v2 GA. | SQLAlchemy 2 async + Pydantic v2 schemas |
| psycopg2 | Sync-only PostgreSQL driver. Will block the event loop in async FastAPI routes. | asyncpg |
| requests | Sync HTTP client. Blocks the event loop. Used in sync tests only. | httpx |
| pip + requirements.txt | Slower, no lock file semantics, no dependency resolver with conflict detection. | uv |
| FastMCP v1 (jlowin/fastmcp) | Superseded by the official MCP Python SDK rebranded as FastMCP v2. The v1 API is different and unmaintained. Verify you are installing from the correct PyPI package (`fastmcp`). | fastmcp 2.x |

---

## Stack Patterns by Variant

**If deploying on a VPS (most likely for bigcattechlab.com):**
- Use Docker + docker-compose for local parity
- Single container: Uvicorn serving FastAPI + FastMCP on one port (e.g., 8000)
- Nginx reverse proxy in front: handles TLS, forwards to uvicorn
- PostgreSQL in a separate Docker container or managed DB service

**If the MCP interface needs authentication (likely for agent write actions):**
- Require Auth0 bearer token on `/mcp` routes
- Implement as ASGI middleware on the mounted sub-app
- Do NOT expose unauthenticated MCP write tools — agents can trigger project actions

**If blog post volume grows significantly:**
- Add Redis for response caching (`fastapi-cache2` with Redis backend)
- For current scope (personal portfolio), in-memory or no caching is fine

---

## Version Compatibility

| Package | Compatible With | Notes |
|---------|-----------------|-------|
| FastAPI 0.115.x | Pydantic 2.x | FastAPI 0.100+ dropped Pydantic v1 support entirely. Do not mix. |
| SQLAlchemy 2.x | asyncpg 0.29.x | The `postgresql+asyncpg://` dialect requires asyncpg to be installed separately. |
| Alembic 1.13.x | SQLAlchemy 2.x | Alembic 1.13+ is required for full SQLAlchemy 2.0 support. Do not use Alembic 1.12 or earlier. |
| python-jose 3.3.x | cryptography 42.x | python-jose uses `cryptography` as the RS256 backend. Verify compatibility if cryptography auto-upgrades. |
| pytest-asyncio 0.23.x | pytest 8.x | 0.23+ is required for pytest 8 compatibility and the `asyncio_mode = "auto"` config option. |
| FastMCP 2.x | FastAPI 0.110.x+ | FastMCP v2 requires a relatively recent FastAPI for the ASGI mount API. Confirm in FastMCP release notes. |

---

## Sources

- Training data (knowledge cutoff August 2025) — FastAPI architecture, SQLAlchemy 2 async patterns, Auth0 FastAPI JWT pattern
- https://pypi.org/project/fastapi/ — VERIFY current version (WebFetch denied during session)
- https://pypi.org/project/fastmcp/ — VERIFY current version and v2 API stability
- https://pypi.org/project/sqlalchemy/ — VERIFY current version
- https://pypi.org/project/alembic/ — VERIFY current version
- https://fastmcp.readthedocs.io/ or https://github.com/jlowin/fastmcp — VERIFY FastAPI mount pattern is still correct in current release
- https://auth0.com/docs/quickstart/backend/python — VERIFY recommended JWT validation library
- https://docs.astral.sh/uv/ — uv documentation (MEDIUM confidence on uv as standard — was rapidly gaining adoption as of Aug 2025)

**All version numbers should be treated as MEDIUM confidence.** Before writing `pyproject.toml`, run `pip index versions [package]` or check PyPI for each package's current stable release.

---

*Stack research for: Python FastAPI + FastMCP + Auth0 + PostgreSQL portfolio backend*
*Researched: 2026-03-25*
