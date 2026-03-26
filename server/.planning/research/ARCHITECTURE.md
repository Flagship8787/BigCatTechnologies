# Architecture Research

**Domain:** FastAPI + FastMCP personal portfolio backend
**Researched:** 2026-03-25
**Confidence:** MEDIUM — FastAPI router patterns are HIGH (official docs). FastMCP ASGI mounting is MEDIUM (training data, August 2025 cutoff; official docs were inaccessible during this research session). Auth0 JWT dependency pattern is MEDIUM (established community pattern, official docs inaccessible).

## Standard Architecture

### System Overview

```
┌───────────────────────────────────────────────────────────────────┐
│                          Incoming Traffic                          │
│         Browser / Frontend          AI Agents (MCP clients)       │
└───────────────────┬─────────────────────────┬─────────────────────┘
                    │ HTTP REST               │ MCP Protocol (SSE or stdio)
                    ▼                         ▼
┌───────────────────────────────────────────────────────────────────┐
│                        FastAPI Application                         │
│  ┌────────────────────┐          ┌────────────────────────────┐   │
│  │   REST API Layer   │          │     MCP Layer (FastMCP)    │   │
│  │                    │          │  mounted at /mcp           │   │
│  │  /api/v1/blog      │          │  Tools: read_blog_post,    │   │
│  │  /api/v1/projects  │          │         list_projects,     │   │
│  │  /api/v1/resume    │          │         get_resume,        │   │
│  │  /admin/...        │          │         trigger_action     │   │
│  └────────┬───────────┘          └────────────┬───────────────┘   │
│           │                                   │                   │
│  ┌────────▼───────────────────────────────────▼───────────────┐   │
│  │                   Auth0 JWT Middleware                      │   │
│  │  (Dependency-injected on protected routes; MCP tools that  │   │
│  │   write data also validate bearer token)                   │   │
│  └────────────────────────────┬───────────────────────────────┘   │
│                               │                                   │
│  ┌────────────────────────────▼───────────────────────────────┐   │
│  │                     Service Layer                          │   │
│  │  BlogService  |  ProjectService  |  ResumeService          │   │
│  └────────────────────────────┬───────────────────────────────┘   │
│                               │                                   │
│  ┌────────────────────────────▼───────────────────────────────┐   │
│  │              Database Layer (SQLAlchemy + Alembic)         │   │
│  │  BlogPost model  |  Project model  |  Resume model/JSON    │   │
│  └────────────────────────────────────────────────────────────┘   │
└───────────────────────────────────────────────────────────────────┘
                               │
                    ┌──────────▼──────────┐
                    │  PostgreSQL / SQLite │
                    └─────────────────────┘
```

### Component Responsibilities

| Component | Responsibility | Notes |
|-----------|----------------|-------|
| FastAPI app (`main.py`) | Application entry point; mounts MCP sub-app; includes REST routers | Single ASGI app process |
| REST routers (`routers/`) | Handle HTTP CRUD endpoints; validate inputs via Pydantic; call services | One router module per domain (blog, projects, resume) |
| MCP layer (`mcp/`) | FastMCP server; exposes tools and resources for AI agent consumption | Mounted as ASGI sub-app at `/mcp` |
| Auth0 middleware / dependency | Validates Auth0-issued JWTs on write routes and admin routes | FastAPI `Depends()` pattern — not global middleware |
| Service layer (`services/`) | Business logic; called by both REST routers and MCP tools | Single source of truth; keeps MCP tools thin |
| SQLAlchemy models (`models/`) | ORM models for blog posts, projects, resume | Alembic for migrations |
| Pydantic schemas (`schemas/`) | Request/response validation; serialization shapes | Separate from ORM models |
| Config (`core/config.py`) | Settings from environment via `pydantic-settings` | DB URL, Auth0 domain/audience, secrets |

## Recommended Project Structure

```
server/
├── app/
│   ├── main.py                  # FastAPI app factory; mounts MCP; includes routers
│   ├── core/
│   │   ├── config.py            # Settings (pydantic-settings, reads env vars)
│   │   ├── database.py          # SQLAlchemy engine, session factory
│   │   └── auth.py              # Auth0 JWT validation dependency
│   ├── routers/
│   │   ├── blog.py              # GET/POST/PUT/DELETE /api/v1/blog/...
│   │   ├── projects.py          # GET/POST/PUT/DELETE /api/v1/projects/...
│   │   └── resume.py            # GET/PUT /api/v1/resume
│   ├── mcp/
│   │   ├── server.py            # FastMCP server instance; tool registrations
│   │   ├── tools/
│   │   │   ├── blog_tools.py    # MCP tools: read_post, list_posts
│   │   │   ├── project_tools.py # MCP tools: list_projects, get_project
│   │   │   └── resume_tools.py  # MCP tools: get_resume
│   │   └── resources/
│   │       └── site_resources.py # MCP resources (optional static content)
│   ├── services/
│   │   ├── blog_service.py      # CRUD logic for blog posts
│   │   ├── project_service.py   # CRUD logic for projects
│   │   └── resume_service.py    # Logic for resume read/update
│   ├── models/
│   │   ├── blog.py              # BlogPost SQLAlchemy model
│   │   ├── project.py           # Project SQLAlchemy model
│   │   └── resume.py            # Resume SQLAlchemy model (or JSON column)
│   └── schemas/
│       ├── blog.py              # BlogPostCreate, BlogPostRead, BlogPostUpdate
│       ├── project.py           # ProjectCreate, ProjectRead, ProjectUpdate
│       └── resume.py            # ResumeRead, ResumeUpdate
├── alembic/                     # DB migrations
│   ├── env.py
│   └── versions/
├── tests/
│   ├── test_blog.py
│   ├── test_projects.py
│   └── test_mcp.py
├── pyproject.toml               # Dependencies (fastapi, fastmcp, sqlalchemy, etc.)
├── alembic.ini
└── .env                         # Local env vars (not committed)
```

### Structure Rationale

- **`routers/`:** One file per domain resource. Each router uses `APIRouter(prefix="/api/v1/resource", tags=["resource"])`. Public read routes have no auth dependency; write routes inject `Depends(verify_token)`.
- **`mcp/`:** Isolated from REST layer. MCP tools call service layer functions directly — they do not call REST route handlers. This prevents double-serialization and keeps MCP tools thin.
- **`services/`:** The service layer is the only code that touches the database. Both REST routers and MCP tools call services. This is the key architectural boundary that prevents duplication.
- **`schemas/`:** Pydantic schemas are separate from SQLAlchemy models. REST responses serialize through schemas; MCP tools return plain dicts or simple types directly.
- **`core/`:** Central config, DB session, and auth dependency. Everything imports from here.

## Architectural Patterns

### Pattern 1: FastMCP Mounted as ASGI Sub-Application

**What:** FastMCP creates its own ASGI app, which is mounted onto the FastAPI application at a fixed path prefix (e.g., `/mcp`). The MCP server runs in the same process as the REST API.

**When to use:** Always for this project — single process simplifies deployment and lets MCP tools share DB sessions and services with REST routes.

**Trade-offs:** Simple deployment; shared memory; MCP and REST can share config. Downside: if MCP traffic spikes, it can affect REST latency (not a concern at personal-project scale).

**Example (MEDIUM confidence — verify against current FastMCP docs):**
```python
# app/main.py
from fastapi import FastAPI
from fastmcp import FastMCP
from app.mcp.server import mcp_server
from app.routers import blog, projects, resume

app = FastAPI(title="BigCatTechLab API")

# Mount MCP as ASGI sub-app at /mcp
# FastMCP v2+ exposes .asgi_app() or similar — verify exact API
app.mount("/mcp", mcp_server.get_asgi_app())

# REST routers
app.include_router(blog.router)
app.include_router(projects.router)
app.include_router(resume.router)
```

```python
# app/mcp/server.py
from fastmcp import FastMCP
from app.mcp.tools import blog_tools, project_tools, resume_tools

mcp_server = FastMCP(name="BigCatTechLab")

# Register tools from each domain module
blog_tools.register(mcp_server)
project_tools.register(mcp_server)
resume_tools.register(mcp_server)
```

### Pattern 2: Auth0 JWT as FastAPI Dependency (Not Global Middleware)

**What:** Auth validation is a `Depends()` injected only on routes that need it. Public read routes have no auth. Admin write routes get `Depends(verify_token)` at the router level.

**When to use:** Always preferred over global middleware in FastAPI — keeps public routes fast and makes auth intent explicit per-route.

**Trade-offs:** More explicit (good); requires every protected router to declare the dependency (acceptable overhead).

**Example (MEDIUM confidence — established FastAPI/Auth0 community pattern):**
```python
# app/core/auth.py
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
from app.core.config import settings

security = HTTPBearer()

async def verify_token(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> dict:
    token = credentials.credentials
    try:
        payload = jwt.decode(
            token,
            settings.auth0_public_key,  # fetched from Auth0 JWKS endpoint
            algorithms=["RS256"],
            audience=settings.auth0_audience,
            issuer=f"https://{settings.auth0_domain}/"
        )
        return payload
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
```

```python
# app/routers/blog.py
from fastapi import APIRouter, Depends
from app.core.auth import verify_token

router = APIRouter(prefix="/api/v1/blog", tags=["blog"])

@router.get("/")          # Public — no auth
async def list_posts(): ...

@router.post("/", dependencies=[Depends(verify_token)])   # Admin only
async def create_post(): ...
```

### Pattern 3: Shared Service Layer (DRY Between REST and MCP)

**What:** Service functions contain all business logic and DB operations. Both REST route handlers and MCP tools call the same service functions. Neither layer duplicates logic.

**When to use:** Essential when the same data (blog posts, projects, resume) is accessible via both REST and MCP. Without this, any logic change requires two updates.

**Trade-offs:** Adds one layer of indirection; keeps system maintainable as both REST and MCP surfaces grow.

**Example:**
```python
# app/services/blog_service.py
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.blog import BlogPost
from app.schemas.blog import BlogPostCreate

async def get_all_posts(db: AsyncSession) -> list[BlogPost]:
    ...

async def get_post_by_slug(db: AsyncSession, slug: str) -> BlogPost | None:
    ...

# app/routers/blog.py  — REST handler calls service
@router.get("/{slug}")
async def read_post(slug: str, db: AsyncSession = Depends(get_db)):
    return await blog_service.get_post_by_slug(db, slug)

# app/mcp/tools/blog_tools.py  — MCP tool also calls same service
@mcp_server.tool()
async def read_blog_post(slug: str) -> dict:
    async with get_db_session() as db:
        post = await blog_service.get_post_by_slug(db, slug)
        return post.to_dict() if post else {"error": "not found"}
```

## Data Flow

### Public REST Read Request (e.g., browser fetching blog posts)

```
Browser GET /api/v1/blog/
    ↓
FastAPI routes to blog router
    ↓
blog.list_posts() handler
    ↓
blog_service.get_all_posts(db)
    ↓
SQLAlchemy query → PostgreSQL
    ↓
SQLAlchemy ORM objects
    ↓
Pydantic BlogPostRead schema serialization
    ↓
JSON HTTP response → Browser
```

### Admin Write Request (e.g., creating a blog post)

```
POST /api/v1/blog/ + Authorization: Bearer <token>
    ↓
FastAPI routes to blog router
    ↓
verify_token dependency runs → validates JWT with Auth0 JWKS
    ↓
    ├── 401 if invalid → response ends here
    └── payload passed to handler
blog.create_post(post_in, token_payload, db) handler
    ↓
blog_service.create_post(db, post_in)
    ↓
SQLAlchemy insert → PostgreSQL
    ↓
New BlogPost ORM object
    ↓
Pydantic BlogPostRead schema serialization
    ↓
201 JSON response
```

### AI Agent MCP Request (e.g., Claude reading blog posts)

```
MCP client connects to /mcp (SSE transport)
    ↓
FastMCP handles MCP protocol handshake
    ↓
Agent calls tool: read_blog_post(slug="my-post")
    ↓
FastMCP dispatches to registered tool function
    ↓
blog_service.get_post_by_slug(db, slug)   ← same service as REST
    ↓
SQLAlchemy query → PostgreSQL
    ↓
dict response returned to MCP client
    ↓
Agent receives structured content
```

### Key Data Flows

1. **REST reads and MCP reads converge at the service layer** — the database is never accessed directly from routers or MCP tools.
2. **Auth0 token validation is stateless** — FastAPI dependency fetches the Auth0 JWKS public key (cached) and validates the JWT locally without an Auth0 API call per request.
3. **MCP tools are read-heavy by default** — write tools (e.g., `trigger_action`) should also validate a bearer token passed as a tool argument or via MCP transport-level auth, since FastAPI's `Depends()` does not apply inside FastMCP tools.

## Scaling Considerations

| Scale | Architecture Adjustments |
|-------|--------------------------|
| Personal site (1-100 users) | Single process, SQLite acceptable, no caching needed |
| Small public traffic (100-10k) | PostgreSQL, add response caching via `fastapi-cache2` on read routes |
| Higher load (10k+) | Out of scope for this project; would need async connection pooling, read replicas |

### Scaling Priorities

1. **First bottleneck:** Database connections under concurrent MCP + REST load. Fix: async SQLAlchemy with connection pool (`asyncpg`).
2. **Second bottleneck:** Auth0 JWKS key fetching. Fix: cache the JWKS response (standard pattern — `python-jose` handles this with a cache TTL).

## Anti-Patterns

### Anti-Pattern 1: MCP Tools That Duplicate REST Logic

**What people do:** Copy-paste route handler code into MCP tool functions.
**Why it's wrong:** Any change to business logic requires updating two places. Logic drift causes inconsistent behavior between REST and MCP surfaces.
**Do this instead:** Both REST handlers and MCP tools call the service layer. The service layer is the single source of truth.

### Anti-Pattern 2: Global Auth Middleware on All Routes

**What people do:** Apply Auth0 JWT validation as a global FastAPI middleware so every request is authenticated.
**Why it's wrong:** Public read endpoints (blog, projects, resume) should be accessible without auth. Global middleware breaks public APIs.
**Do this instead:** Use `Depends(verify_token)` at the router or route level only on routes that require authentication.

### Anti-Pattern 3: Putting FastMCP on the Same Router Path as REST

**What people do:** Try to integrate MCP protocol handling inside a FastAPI route handler.
**Why it's wrong:** FastMCP is itself an ASGI application. Trying to call it from within a route handler fights the framework and breaks SSE streaming.
**Do this instead:** Mount FastMCP as an ASGI sub-application using `app.mount("/mcp", mcp_server.get_asgi_app())`. It handles its own request lifecycle independently.

### Anti-Pattern 4: SQLAlchemy Models as API Response Types

**What people do:** Return ORM model instances directly from route handlers.
**Why it's wrong:** Exposes internal schema, breaks when lazy-loaded relationships are accessed outside session context, and makes API contract implicit.
**Do this instead:** Always serialize through Pydantic schemas. Define `BlogPostRead`, `ProjectRead` schemas explicitly.

### Anti-Pattern 5: MCP Write Tools Without Auth

**What people do:** Expose MCP tools that can modify data (create post, update project) without any authentication check inside the tool.
**Why it's wrong:** FastAPI's `Depends()` auth system does not protect FastMCP tools — they are called through the MCP protocol, not through HTTP route handlers.
**Do this instead:** MCP tools that perform writes should require a token argument or implement transport-level auth. For v1, limit MCP tools to read-only operations.

## Integration Points

### External Services

| Service | Integration Pattern | Notes |
|---------|---------------------|-------|
| Auth0 | JWT validation via JWKS endpoint (`/.well-known/jwks.json`); validated locally per request | Use `python-jose` or `authlib`; cache JWKS with TTL |
| PostgreSQL | Async SQLAlchemy + asyncpg driver | `DATABASE_URL` from env; Alembic for migrations |

### Internal Boundaries

| Boundary | Communication | Notes |
|----------|---------------|-------|
| REST routers ↔ Services | Direct async function calls | Routers inject DB session; services receive it as parameter |
| MCP tools ↔ Services | Direct async function calls | MCP tools manage their own DB session via context manager |
| FastAPI app ↔ FastMCP | ASGI mount (`app.mount`) | FastMCP handles its own request lifecycle after the mount point |
| MCP tools ↔ REST routers | No direct communication | Both talk to services; they never call each other |

## Suggested Build Order

Build in this order to respect dependencies and enable incremental testing:

1. **Core foundation** — `core/config.py`, `core/database.py`, DB connection verified. No business logic yet.
2. **ORM models + migrations** — `models/blog.py`, `models/project.py`, `models/resume.py` with Alembic initial migration. Tables exist before any service code.
3. **Service layer** — `services/blog_service.py`, etc. Unit-testable without HTTP or MCP layer.
4. **Pydantic schemas** — `schemas/blog.py`, etc. Defined once; shared by REST and MCP.
5. **REST routers (read-only first)** — GET endpoints only. Validates service layer works end-to-end through HTTP.
6. **Auth0 dependency** — `core/auth.py`. Add `Depends(verify_token)` to write routes once reads are working.
7. **REST write routes** — POST/PUT/DELETE endpoints with auth. Full REST CRUD now functional.
8. **FastMCP server + tools** — `mcp/server.py` and `mcp/tools/`. Mounts onto the FastAPI app. Read-only tools first; they call the already-tested service layer.
9. **MCP write tools (optional v2)** — Only after read tools are proven. Requires explicit auth strategy for MCP writes.

## Sources

- FastAPI official docs — "Bigger Applications" router pattern: https://fastapi.tiangolo.com/tutorial/bigger-applications/ (HIGH confidence — fetched directly)
- FastMCP ASGI mounting pattern: training data, August 2025 cutoff (MEDIUM confidence — official docs were inaccessible; verify against https://gofastmcp.com/deployment/asgi before implementing)
- Auth0 JWT dependency pattern for FastAPI: established community pattern (MEDIUM confidence — verify against https://auth0.com/docs/quickstart/backend/python)
- SQLAlchemy async pattern with FastAPI: https://fastapi.tiangolo.com/tutorial/sql-databases/ (pattern well-established; verify async specifics)

---
*Architecture research for: FastAPI + FastMCP personal portfolio backend*
*Researched: 2026-03-25*
