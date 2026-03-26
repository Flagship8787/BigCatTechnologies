# Project Research Summary

**Project:** BigCatTechnologies Server
**Domain:** FastAPI + FastMCP personal portfolio/hub backend with Auth0 SSO and PostgreSQL
**Researched:** 2026-03-25
**Confidence:** MEDIUM (no live web access during research; all findings from training data through August 2025)

## Executive Summary

BigCatTechnologies Server is a personal portfolio backend with a genuine differentiator: a Model Context Protocol (MCP) interface that lets AI agents (Claude, Cursor) read and eventually act on the owner's content. The recommended approach is a single Python process running FastAPI for HTTP REST endpoints alongside FastMCP mounted as an ASGI sub-application at `/mcp`. Both surfaces share a service layer that sits in front of an async SQLAlchemy + PostgreSQL database, eliminating logic duplication. Auth0 JWT validation gates all write operations using FastAPI's dependency injection, while public read routes require no authentication. This architecture is well-understood, has strong community precedent, and is deployable as a single Docker container behind nginx.

The core build order is dictated by hard dependencies: config and secrets management must come first (before any code is committed), followed by the database layer (models and migrations), then the shared service layer, then REST routes, then Auth0 auth, and finally the FastMCP mount. The MCP layer is the last thing added because it depends on everything else being correct first — MCP tools are thin wrappers over already-tested services. This order also maps directly to the pitfall profile: the most dangerous mistakes cluster in the earliest phases (secrets management, async database setup, Auth0 configuration) and must be addressed before any feature work begins.

The primary risk in this project is the FastMCP auth boundary. FastAPI's dependency injection does not propagate into a mounted ASGI sub-application, so MCP routes require a separate auth enforcement mechanism. This is a non-obvious failure mode that looks correct until explicitly tested. The mitigation is clear: MCP write tools should be deferred until a verified auth strategy for the MCP transport layer is in place, and every phase touching auth or MCP integration needs explicit tests that confirm unauthorized access is rejected — not just that authorized access works.

## Key Findings

### Recommended Stack

The stack centers on Python 3.12, FastAPI 0.115.x, and FastMCP 2.x. FastMCP v2 introduced an ASGI mount pattern (`app.mount("/mcp", mcp_server.get_asgi_app())`) that colocates the MCP server with the REST API in a single process — this is the definitive integration approach and eliminates the operational overhead of a separate MCP process or port. The database layer uses SQLAlchemy 2.x async API (`AsyncSession`, `asyncpg` driver) against PostgreSQL 16; the async requirement is non-negotiable since sync ORM calls inside `async def` handlers will block the event loop under any real concurrency. Alembic manages all schema migrations. `pydantic-settings` handles environment-based configuration. `uv` replaces pip/poetry as the package manager. All version numbers should be confirmed against PyPI before writing `pyproject.toml` — versions in STACK.md are from training data.

**Core technologies:**
- Python 3.12: Runtime — maximum ecosystem compatibility; 3.13 too new for some libraries
- FastAPI 0.115.x: HTTP API framework — native async, Pydantic v2, OpenAPI auto-generation
- FastMCP 2.x: MCP server layer — ASGI mount onto FastAPI shares process and services
- PostgreSQL 16.x: Primary database — ACID guarantees, async driver support, no SQLite in VPS production
- SQLAlchemy 2.x (async): ORM + query layer — full async API, Alembic integration, typed mapped classes
- asyncpg: PostgreSQL async driver — required for non-blocking DB access in async handlers
- Alembic 1.13.x: Database migrations — autogenerate from models, mandatory in production
- python-jose 3.3.x: JWT validation — JWKS fetching and RS256 verification for Auth0 tokens
- pydantic-settings 2.x: Configuration — environment variable loading with type validation
- uv: Package manager — dramatically faster than pip/poetry, becoming community default

### Expected Features

The feature set serves two audiences: human visitors accessing REST endpoints and AI agents connecting via MCP. Both have non-negotiable baselines. Research identifies tags (blog and project) as P1 — they appear low-priority but directly enable meaningful agent queries like "what projects use FastAPI?", making the MCP interface substantially more useful from day one at very low implementation cost.

**Must have (table stakes):**
- Public read API: GET /posts, /posts/{slug}, /projects, /projects/{id}, /resume — human visitor baseline
- Admin CRUD: POST/PUT/DELETE for posts, projects, resume — owner manages content
- Auth0 JWT verification — gates all write routes
- Health endpoint — deployment infrastructure requires it
- MCP server mounted on FastAPI — agents can connect
- MCP resources: blog posts, projects, resume — agents read content via URI-addressed resources
- Blog post tags + project tech tags — enables precise agent queries from day one

**Should have (competitive):**
- MCP tool: search/filter content — agents query rather than list-then-filter; add when agent usage patterns reveal the need
- MCP prompts: canned prompts (summarize recent work, find projects by tech, draft blog post) — first-class MCP primitives that make agent workflows reusable
- Auth-gated MCP write tools (create draft post) — owner uses agents as admin interface
- Structured resume following JSON Resume schema (jsonresume.org) — widely understood by frontends and agents

**Defer (v2+):**
- MCP tools: per-project actions (run demo, get status, trigger command) — highest-value eventually, but each integration is bespoke; design the registry pattern first
- Extensible project integration registry — the formal pattern for onboarding new projects without restructuring; needed before the second project integration
- RSS feed — trivial to add later; no readership yet to serve

**Anti-features to reject:** visitor accounts, comments system, WebSocket real-time features, file/media upload API, full-text search engine (PostgreSQL FTS is sufficient at this scale), multi-user admin, versioned post history, MCP sampling.

### Architecture Approach

The architecture follows a layered pattern with a critical constraint: both REST routers and MCP tools call the same service layer and never communicate directly with each other. This single source of truth at the service layer prevents logic drift when the same data (blog posts, projects, resume) is served via two protocols. REST routers handle HTTP CRUD, injecting auth via `Depends(verify_token)` on write routes only. The FastMCP server is mounted as an ASGI sub-application at `/mcp`, outside FastAPI's dependency injection tree. Pydantic schemas are kept separate from SQLAlchemy models. Configuration flows from environment variables through `pydantic-settings` in `core/config.py`. Build order follows strict dependency sequencing: config → models/migrations → services → schemas → REST reads → auth → REST writes → MCP tools.

**Major components:**
1. `core/` (config, database, auth) — foundation; everything imports from here; must exist before any business logic
2. `models/` + `schemas/` — ORM models (SQLAlchemy) and API shapes (Pydantic); separate concerns; Alembic drives all schema changes
3. `services/` (BlogService, ProjectService, ResumeService) — single source of truth; called by both REST routers and MCP tools
4. `routers/` (blog, projects, resume) — HTTP CRUD; public routes unauthenticated; write routes inject `Depends(verify_token)`
5. `mcp/` (server, tools, resources) — FastMCP mounted at `/mcp`; tools are thin wrappers over services; auth enforced at ASGI middleware level, not via FastAPI `Depends()`

### Critical Pitfalls

1. **FastAPI `Depends()` does not protect mounted MCP routes** — FastMCP's ASGI sub-app is outside the DI tree; add auth as ASGI middleware scoped to `/mcp/*` paths; verify with `curl` without a token — the MCP route must return 401
2. **Auth0 audience and issuer misconfiguration** — use the Auth0 API Identifier (not the client ID) as `AUTH0_AUDIENCE`; construct issuer as `f"https://{AUTH0_DOMAIN}/"` with a trailing slash; test with a foreign-app token that should be rejected
3. **JWKS fetched on every request** — initialize `PyJWKClient` once at application startup (module-level or lifespan), not inside the dependency function; per-request JWKS fetching adds 50-200ms latency and triggers Auth0 rate limits
4. **Sync ORM blocking the async event loop** — use `create_async_engine` + `AsyncSession` + `asyncpg` throughout; a single sync ORM call inside `async def` serializes all concurrent requests; verify with a 10-concurrent-request load test
5. **Secrets committed to git** — add `.env` to `.gitignore` before the first commit, not after; provide `.env.example` with placeholders; run `git ls-files .env` as a CI check; this repo is likely public

## Implications for Roadmap

Based on research, the architecture's dependency chain and pitfall clustering point clearly to a 4-phase build sequence. The key insight is that security and data foundation issues are catastrophic if not addressed early — not just annoying — so the first phase is deliberately unglamorous.

### Phase 1: Foundation (Config, Secrets, CORS, Project Scaffold)

**Rationale:** Three of the most expensive pitfalls (secrets in git, CORS wildcard in production, Auth0 misconfiguration) must be addressed before any feature code is written. This phase has no deliverable features but eliminates all "looks done but isn't" foundation failures. Build order from ARCHITECTURE.md starts here: `core/config.py`, `.gitignore`, `.env.example`.
**Delivers:** Project scaffold with `uv`, `pyproject.toml`, Docker setup, `pydantic-settings` config class reading all secrets from environment, `.gitignore` confirming `.env` is excluded, CORS configured with `ALLOWED_ORIGINS` env var, health endpoint, CI skeleton.
**Addresses:** Health endpoint (table stakes), environment configuration
**Avoids:** Secrets committed to git (Pitfall 10), CORS wildcard in production (Pitfall 6), version confusion (verify all package versions against PyPI at scaffold time)

### Phase 2: Database Layer (Models, Migrations, Async Session)

**Rationale:** All features depend on the database. The async ORM pattern must be established correctly before any service code is written — retrofitting sync-to-async is painful. Alembic must be wired into the deployment entrypoint before the first migration, not after.
**Delivers:** SQLAlchemy async engine + `AsyncSession` factory, `BlogPost`, `Project`, `Resume` ORM models, Alembic initial migration, Docker entrypoint running `alembic upgrade head` before server start, database connection verified via test.
**Uses:** SQLAlchemy 2.x async, asyncpg, Alembic 1.13.x, PostgreSQL 16.x
**Implements:** Database layer component from ARCHITECTURE.md
**Avoids:** Sync ORM blocking event loop (Pitfall 8), migrations not in deployment (Pitfall 7), `Base.metadata.create_all()` in production

### Phase 3: REST API + Auth (Service Layer, Public Reads, Auth0, Admin Writes)

**Rationale:** Build the service layer first (unit-testable without HTTP), then read routes (validate service layer end-to-end), then Auth0 auth dependency, then write routes. This sequencing lets each layer be validated before the next is added. Tags are included here — they cost very little and enable meaningful MCP queries in Phase 4.
**Delivers:** `BlogService`, `ProjectService`, `ResumeService`; Pydantic schemas; public GET endpoints for posts/projects/resume (with tag filtering); Auth0 JWT dependency with JWKS caching; admin POST/PUT/DELETE endpoints; integration test confirming foreign-app token is rejected.
**Addresses:** All P1 table stakes features from FEATURES.md (public read API, admin CRUD, auth, blog/project tags)
**Avoids:** Auth0 audience mismatch (Pitfall 1), issuer trailing slash (Pitfall 2), JWKS per-request fetching (Pitfall 3), ORM models returned directly as responses (Architecture Anti-Pattern 4)

### Phase 4: MCP Interface (FastMCP Mount, Resources, Read Tools)

**Rationale:** MCP is last because it depends on all of Phase 3 being correct. MCP tools are thin wrappers over already-tested services — most of the work is already done. Auth for MCP routes must be implemented at the ASGI middleware layer, not via FastAPI `Depends()`. Defer write tools until the auth strategy for MCP transport is verified.
**Delivers:** FastMCP server mounted at `/mcp`; MCP resources for blog posts, projects, resume; read-only MCP tools calling service layer; ASGI middleware enforcing auth on `/mcp` paths; integration test confirming unauthenticated MCP requests return 401; MCP prompts (summarize recent work, find projects by tech).
**Addresses:** MCP server mount, MCP resources (P1 from FEATURES.md), MCP prompts (P2 from FEATURES.md)
**Avoids:** FastAPI DI not protecting MCP routes (Pitfall 4), MCP tool exceptions crashing agent session (Pitfall 9), MCP tools duplicating REST logic (Architecture Anti-Pattern 1), FastMCP mounted inside route handler (Architecture Anti-Pattern 3)

### Phase 5: MCP Write Tools + Agent Admin Interface (Post-Validation)

**Rationale:** Only add MCP write tools after Phase 4 is proven in real agent interactions. Write tools require scope-based authorization (not just token presence) and a verified strategy for forwarding bearer tokens through the MCP transport layer.
**Delivers:** Auth-gated MCP write tools (create draft post); Auth0 scope enforcement (`write:content` / `admin`) in tool handlers; search/filter content tool; read-only token confirmed to be rejected by write tools.
**Addresses:** Auth-gated MCP write tools, MCP search tool (P2 from FEATURES.md)
**Avoids:** Write tools accessible to any valid token (Pitfall 5), scope checks skipped on MCP tools (Security Mistakes section from PITFALLS.md)

### Phase Ordering Rationale

- Phases 1-2 are foundation work with no user-visible features — they exist entirely to prevent catastrophic mistakes identified in PITFALLS.md. Skipping them to get to features faster is the canonical way to ship a broken backend.
- Phase 3 builds the complete REST surface first because it is architecturally independent of FastMCP and can be fully validated before the MCP layer is added.
- Phase 4 follows naturally: MCP tools are thin wrappers over Phase 3's service layer; nearly all the work is already done.
- Phase 5 is explicitly post-validation because write tools require auth strategies that need real agent interaction to verify. The pitfall risk is highest here.
- The project integration registry (enabling per-project MCP actions) is a v2+ concern and should not be in scope until at least one real project integration exists to inform the registry design.

### Research Flags

Phases likely needing deeper research during planning:
- **Phase 4 (FastMCP Auth):** The exact mechanism for enforcing auth on FastMCP-mounted ASGI sub-apps was evolving rapidly as of August 2025. Before implementing, verify against current FastMCP docs at gofastmcp.com — specifically, whether FastMCP v2.x provides a first-class auth hook or whether ASGI middleware wrapping is still required.
- **Phase 5 (MCP Write Tool Auth):** How bearer tokens are forwarded through MCP transport to tool handlers is the least-documented integration point in this stack. This needs verification against current FastMCP transport documentation before any write tools are built.

Phases with standard patterns (can proceed without research-phase):
- **Phase 1 (Scaffold):** uv, pyproject.toml, Docker setup, pydantic-settings — all well-documented and stable.
- **Phase 2 (Database):** SQLAlchemy 2.x async + asyncpg + Alembic is a mature, well-documented combination with abundant FastAPI examples.
- **Phase 3 (REST + Auth0):** FastAPI dependency injection + Auth0 RS256 JWT validation is a widely-documented community pattern. The Auth0 FastAPI quickstart is authoritative.

## Confidence Assessment

| Area | Confidence | Notes |
|------|------------|-------|
| Stack | MEDIUM | Core FastAPI/SQLAlchemy patterns are HIGH confidence; FastMCP v2 API specifics are MEDIUM — verify mount API against current docs |
| Features | MEDIUM | Table stakes features are HIGH confidence (stable domain); MCP-specific features are MEDIUM — MCP spec is stable but FastMCP decorator API should be verified |
| Architecture | MEDIUM | FastAPI router patterns are HIGH; FastMCP ASGI mount and MCP auth boundary are MEDIUM — key details need verification against current FastMCP docs |
| Pitfalls | MEDIUM | Auth0 JWT pitfalls are HIGH confidence (stable, well-documented); FastMCP-specific pitfalls are MEDIUM; version-specific behavior may have changed |

**Overall confidence:** MEDIUM

### Gaps to Address

- **FastMCP auth integration:** The mechanism for protecting `/mcp` routes is the most important unresolved question. Before Phase 4 planning, fetch current FastMCP docs and find the documented pattern for auth on mounted sub-apps. Do not assume ASGI middleware wrapping is still necessary if FastMCP now provides a first-class hook.
- **FastMCP v2 exact API:** `mcp_server.get_asgi_app()` is the pattern from training data — confirm the exact method name against current PyPI package. The FastMCP v1-to-v2 migration involved API changes; verify you are on v2 before writing any tool registrations.
- **Package versions:** All version numbers in STACK.md are from training data (August 2025). Run `pip index versions [package]` or check PyPI for each package before writing `pyproject.toml`.
- **JSON Resume schema version:** The jsonresume.org schema version should be confirmed before designing the Resume model — schema fields and required properties may have changed.
- **MCP transport bearer token forwarding:** How an AI agent client forwards an `Authorization` header through SSE or streamable-HTTP MCP transport to a tool handler is under-documented. This must be resolved before Phase 5.

## Sources

### Primary (HIGH confidence)
- FastAPI official docs — router patterns, dependency injection, OAuth2 JWT: https://fastapi.tiangolo.com/tutorial/bigger-applications/
- SQLAlchemy async engine patterns — stable, well-established API
- MCP specification — tools, resources, prompts primitives (training data through August 2025)

### Secondary (MEDIUM confidence)
- FastMCP v2 ASGI mount pattern — training data August 2025; verify at https://gofastmcp.com/deployment/asgi
- Auth0 FastAPI JWT integration pattern — community pattern, verify at https://auth0.com/docs/quickstart/backend/python
- FastMCP tool/resource/prompt decorator API — training data; verify at https://gofastmcp.com
- uv package manager patterns — https://docs.astral.sh/uv/

### Tertiary (LOW confidence)
- JSON Resume schema fields — https://jsonresume.org/schema; confirm current version before adopting
- FastMCP v2 auth hook availability — needs current docs; may have changed significantly since August 2025 training data

---
*Research completed: 2026-03-25*
*Ready for roadmap: yes*
