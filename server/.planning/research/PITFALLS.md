# Pitfalls Research

**Domain:** FastAPI + FastMCP + Auth0 personal portfolio backend
**Researched:** 2026-03-25
**Confidence:** MEDIUM (training data through August 2025; web fetch unavailable during research session)

---

## Critical Pitfalls

### Pitfall 1: Auth0 JWT Audience Mismatch

**What goes wrong:**
JWT validation silently rejects all tokens or raises `InvalidAudienceError` at runtime despite the token appearing valid in the Auth0 dashboard. Every authenticated request returns 401.

**Why it happens:**
Auth0 issues tokens with an `aud` (audience) claim set to the API identifier you configure in the Auth0 dashboard. If `python-jose` or `authlib` is asked to validate against the wrong audience string — or audience validation is skipped entirely — all tokens are rejected. Developers copy example code that hardcodes `aud` as the Auth0 client ID instead of the API identifier (these are different values).

**How to avoid:**
- Set `AUTH0_AUDIENCE` to the exact API identifier string configured in Auth0 dashboard (e.g., `https://api.bigcattechlab.com`), NOT the client ID.
- Pass `audience=AUTH0_AUDIENCE` explicitly to every `jwt.decode()` call.
- Add an integration test that validates a real Auth0 test token against your decode logic before any route is built.

**Warning signs:**
- 401 on every authenticated request even with a fresh token from Auth0.
- `InvalidAudienceError` or `JWTClaimsError` in logs.
- Token decodes fine with `jwt.decode(token, options={"verify_aud": False})` but fails normally.

**Phase to address:** Foundation / Auth setup phase (first phase that wires Auth0)

---

### Pitfall 2: Auth0 Issuer URL Trailing-Slash Mismatch

**What goes wrong:**
JWT validation fails with an issuer mismatch error. The token validates fine in jwt.io but fails in code.

**Why it happens:**
Auth0 issues tokens with `iss` claim set to `https://YOUR_DOMAIN/` (with a trailing slash). Many developers configure `AUTH0_DOMAIN` as `yourdomain.auth0.com` and construct the issuer as `f"https://{AUTH0_DOMAIN}"` (no trailing slash). The comparison `"https://x.auth0.com" != "https://x.auth0.com/"` causes a hard validation failure.

**How to avoid:**
- Always construct the issuer as `f"https://{AUTH0_DOMAIN}/"` (trailing slash required).
- Verify by decoding a real token without verification and checking the `iss` claim value directly.

**Warning signs:**
- `InvalidIssuerError` or `JWTClaimsError: Invalid issuer` in logs.
- Decode works when `verify_iss=False` but fails normally.

**Phase to address:** Foundation / Auth setup phase

---

### Pitfall 3: JWKS Fetched on Every Request (No Caching)

**What goes wrong:**
Every authenticated request makes an HTTP call to `https://YOUR_DOMAIN/.well-known/jwks.json` to fetch the public key. At low traffic this is slow; at moderate traffic it triggers Auth0 rate limits. At high traffic it becomes a hard outage.

**Why it happens:**
Naive implementations call `jwks_client.get_signing_key_from_jwt(token)` without caching the JWKS response. Auth0's Python quickstart examples use `PyJWKClient` which has built-in caching, but developers sometimes roll their own without it or disable caching accidentally.

**How to avoid:**
- Use `PyJWKClient(jwks_uri, cache_keys=True, cache_jwk_set=True)` from the `PyJWT` library. Cache is on by default — don't disable it.
- Set `lifespan_seconds` appropriately (default 300s is fine for most cases).
- Initialize the `PyJWKClient` once at application startup (module-level or via FastAPI lifespan), not inside the dependency function.

**Warning signs:**
- Latency spikes on every authenticated request (10-100ms added per call).
- Auth0 logs show JWKS endpoint being hammered.
- Intermittent 429 errors from Auth0.

**Phase to address:** Foundation / Auth setup phase

---

### Pitfall 4: FastAPI Dependency Doesn't Protect MCP Routes

**What goes wrong:**
The REST API routes are correctly protected with `Depends(get_current_user)`, but the FastMCP-mounted routes bypass auth entirely because FastMCP's ASGI app is mounted without the dependency injected.

**Why it happens:**
When FastMCP is mounted into FastAPI via `app.mount("/mcp", mcp_app)`, the mounted sub-application is outside FastAPI's dependency injection tree. Any `Depends()` guards added to the parent `app` don't propagate into the mounted sub-app. Developers test the `/projects` endpoint (protected), see it work, and assume `/mcp/...` is also protected — it is not.

**How to avoid:**
- Implement auth at the FastMCP level using FastMCP's own middleware hooks or by wrapping the ASGI app in an auth middleware before mounting.
- Alternatively, place auth in a Starlette middleware on the parent `app` and scope it to `/mcp/*` paths explicitly.
- Write an integration test that hits `GET /mcp/...` without a token and asserts a 401 response.

**Warning signs:**
- MCP routes return 200 with no `Authorization` header.
- Running `curl http://localhost:8000/mcp/tools` returns tool list unauthenticated.

**Phase to address:** FastMCP integration phase

---

### Pitfall 5: MCP Tools Expose Write Operations Without Scope Checks

**What goes wrong:**
AI agents (Claude, Cursor, etc.) can invoke MCP tools that create, update, or delete blog posts and projects without any check on whether the calling agent has admin privileges. A misconfigured agent or a prompt injection attack can wipe content.

**Why it happens:**
Auth is treated as binary (authenticated vs not). The MCP interface is "for the owner" so write tools are added without granular scope enforcement. Auth0 access tokens carry scopes (`read:posts`, `write:posts`) but the MCP tool handler never checks them — it only checks that a token is present.

**How to avoid:**
- Define Auth0 API scopes explicitly: `read:content`, `write:content`, `admin`.
- In every MCP tool handler that performs writes, extract the token from context and verify the required scope is present before proceeding.
- Read-only tools (list projects, read blog posts, get resume) can allow any valid token.
- Destructive tools (delete post, update project) require `admin` scope.

**Warning signs:**
- MCP tool handlers do not inspect `token.scopes` or equivalent.
- Any valid Auth0 token (even a read-only one) can invoke write tools.

**Phase to address:** FastMCP integration phase + Security hardening phase

---

### Pitfall 6: CORS Wildcard in Production

**What goes wrong:**
API returns `Access-Control-Allow-Origin: *` in production. The frontend on `bigcattechlab.com` works fine but browsers allow any origin to call the API with credentials, defeating same-origin protection.

**Why it happens:**
`CORSMiddleware(app, allow_origins=["*"])` is copied from the FastAPI docs tutorial to get things working locally and never updated before deployment. Since the portfolio frontend works, it's never noticed.

**How to avoid:**
- Set `allow_origins` to exact allowed origins: `["https://bigcattechlab.com"]`.
- Use an environment variable `ALLOWED_ORIGINS` that is `["*"]` in development and the real domain in production.
- Set `allow_credentials=True` only if cookies are used (not needed for Bearer token auth).

**Warning signs:**
- `allow_origins=["*"]` is present in non-development code.
- No `ALLOWED_ORIGINS` env var separating dev from prod config.

**Phase to address:** Foundation phase (first time CORS is configured)

---

### Pitfall 7: Database Migrations Not Wired Into Deployment

**What goes wrong:**
`alembic upgrade head` is forgotten during deployment. New database schema changes crash the running app. Rolling back requires manual schema surgery.

**Why it happens:**
During development, `alembic upgrade head` is run manually. A deploy script or Dockerfile starts the FastAPI process without running migrations first. This works until the first schema change hits production.

**How to avoid:**
- Add `alembic upgrade head` as a step in the container entrypoint script, before the FastAPI process starts.
- Use `alembic check` in CI to fail the build if there are unmigrated model changes.
- Never use `Base.metadata.create_all()` in production — use Alembic exclusively.

**Warning signs:**
- `Base.metadata.create_all(engine)` present in production app code.
- No migration step in `Dockerfile` or deploy script.
- Alembic `versions/` directory is empty or ignored.

**Phase to address:** Database foundation phase

---

### Pitfall 8: FastAPI Async and Sync ORM Blocking the Event Loop

**What goes wrong:**
Under load, all requests queue up and latency spikes to seconds. The app appears single-threaded even though FastAPI is async.

**Why it happens:**
Using a synchronous ORM (SQLAlchemy sync engine + sync session) inside `async def` route handlers blocks the uvicorn event loop. A single slow query freezes all concurrent requests. This is invisible in development (single user) but surfaces under any real concurrency.

**How to avoid:**
- Use SQLAlchemy's async engine: `create_async_engine(...)` with `AsyncSession`.
- Alternatively, use synchronous routes (`def` instead of `async def`) for database-heavy handlers — FastAPI runs sync routes in a thread pool automatically.
- Never call blocking I/O (file reads, sync HTTP calls, sync ORM queries) from inside `async def` route handlers without `asyncio.run_in_executor`.

**Warning signs:**
- `from sqlalchemy import create_engine` (sync) used in `async def` handlers.
- `Session` (sync) used instead of `AsyncSession`.
- Load test shows linear latency degradation from the first concurrent user.

**Phase to address:** Database foundation phase

---

### Pitfall 9: FastMCP Tool Errors Crash the MCP Session

**What goes wrong:**
An unhandled exception inside an MCP tool handler terminates the entire MCP transport connection. The AI agent loses its session and must reconnect, often losing conversation context.

**Why it happens:**
FastMCP propagates unhandled exceptions from tool handlers up through the transport layer. Developers handle errors in REST routes (returning HTTP 500) but forget that MCP tools need explicit error handling that returns a structured error response rather than raising.

**How to avoid:**
- Wrap every MCP tool handler body in a try/except.
- Return a structured error dict (`{"error": str(e), "success": False}`) rather than raising.
- Log the exception before returning the error response.

**Warning signs:**
- MCP tool handlers have no try/except.
- Agent sessions drop intermittently when tools encounter database errors.

**Phase to address:** FastMCP integration phase

---

### Pitfall 10: Environment Secrets in Code or `.env` Committed to Git

**What goes wrong:**
Auth0 client secret, database URL, or JWT secret key is hardcoded or committed in `.env` to the repository. The portfolio repo is public (common for personal projects), exposing credentials.

**Why it happens:**
Personal projects often skip secret management rigor. `.env` is created locally, works great, and `git add .` captures it before `.gitignore` is set up.

**How to avoid:**
- Add `.env` to `.gitignore` before the first commit — not after.
- Use `python-decouple` or `pydantic-settings` with a `Settings` class that reads from environment variables, with no defaults for secrets.
- Provide a `.env.example` with placeholder values only.
- Run `git secrets` or `trufflehog` in CI to detect accidental commits.

**Warning signs:**
- `.env` is tracked by git (`git ls-files .env` returns output).
- Auth0 domain or client ID is hardcoded as a string literal in source.

**Phase to address:** Foundation phase (before first commit)

---

## Technical Debt Patterns

| Shortcut | Immediate Benefit | Long-term Cost | When Acceptable |
|----------|-------------------|----------------|-----------------|
| `Base.metadata.create_all()` instead of Alembic | No migration setup needed | Schema changes require manual DB surgery in prod | Never in production |
| `allow_origins=["*"]` in CORS | Frontend works immediately | Any origin can call the API | Development only |
| Sync SQLAlchemy in async handlers | Simpler code | Event loop blocking under concurrency | Never; use thread pool or async engine |
| Hardcoded Auth0 config values | Fast initial setup | Credentials in source, config per environment impossible | Never for secrets |
| No MCP tool error handling | Less boilerplate | Agent session drops on any tool failure | Never |
| Skip scope checks on MCP write tools | Simpler auth logic | Any valid token can mutate data | Never for write operations |

---

## Integration Gotchas

| Integration | Common Mistake | Correct Approach |
|-------------|----------------|------------------|
| Auth0 + FastAPI | Validating tokens with the Auth0 client ID as audience | Use the API Identifier (e.g., `https://api.bigcattechlab.com`), not the client ID |
| Auth0 + FastAPI | Fetching JWKS inside the dependency function (per-request) | Initialize `PyJWKClient` once at app startup; it caches keys internally |
| Auth0 + FastAPI | Building issuer as `https://domain` (no trailing slash) | Auth0 `iss` claim always has a trailing slash: `https://domain/` |
| FastMCP + FastAPI | Mounting `mcp_app` and assuming FastAPI `Depends()` protects it | FastMCP sub-app is outside DI tree; add auth at the ASGI middleware layer |
| FastMCP tools | Raising exceptions from tool handlers | Return structured error dict; raised exceptions can break the transport session |
| SQLAlchemy + FastAPI async | `create_engine` (sync) inside `async def` handlers | Use `create_async_engine` + `AsyncSession`, or use `def` routes for DB work |
| Alembic + Docker | Not running `alembic upgrade head` in container startup | Add migration step to entrypoint before starting the server process |
| CORS + Auth0 Bearer | Setting `allow_credentials=True` with `allow_origins=["*"]` | Browsers block this combination; restrict origins or disable credentials flag |

---

## Performance Traps

| Trap | Symptoms | Prevention | When It Breaks |
|------|----------|------------|----------------|
| JWKS fetched per request | 50-200ms latency added to every auth'd request; Auth0 429 errors | Initialize `PyJWKClient` once at startup with caching enabled | From first request |
| Sync ORM in async handlers | Latency scales linearly with concurrent users; requests queue | Use async SQLAlchemy or run sync ORM in thread pool via `run_in_executor` | ~5+ concurrent users |
| No database connection pooling | Connection exhaustion under load; `OperationalError: too many connections` | Use SQLAlchemy's built-in pool (default); set `pool_size` and `max_overflow` appropriately | ~20+ concurrent users |
| N+1 queries in MCP content tools | Listing 50 blog posts triggers 50 separate author/tag queries | Use SQLAlchemy `selectinload` or `joinedload` for relationships | Any list endpoint with relations |

---

## Security Mistakes

| Mistake | Risk | Prevention |
|---------|------|------------|
| Skipping `aud` claim validation | Any Auth0 token from any application works against the API | Always pass `audience=AUTH0_AUDIENCE` to JWT decode |
| MCP write tools accessible to any valid token | Agent or prompt injection can create/delete/modify content | Enforce `write:content` / `admin` scope check in write tool handlers |
| Admin routes lack scope check, only check authentication | Authenticated non-admin tokens can access admin functionality | Check `scope` claim in JWT, not just token presence |
| Exposing internal database IDs in MCP tool responses | Leaks schema internals; enables enumeration attacks | Use UUIDs or slugs as public identifiers; never expose auto-increment integer IDs to agents |
| MCP tool descriptions reveal infrastructure details | Agents (or users inspecting tool schemas) learn server internals | Keep tool descriptions functional ("Create a blog post") not technical ("Inserts into posts table") |
| No rate limiting on MCP endpoints | Agents can invoke tools in tight loops, hammering the database | Add SlowAPI or a reverse-proxy rate limit on `/mcp/*` paths |

---

## "Looks Done But Isn't" Checklist

- [ ] **Auth0 JWT Validation:** Token decodes correctly — but is `aud` claim actually being validated? Verify with a token from a different Auth0 application; it should be rejected.
- [ ] **MCP Auth:** REST routes return 401 without a token — but do MCP routes at `/mcp/...` also return 401? Verify with `curl` without any `Authorization` header.
- [ ] **MCP Write Scope:** Admin MCP tools work with your token — but do they also work with a token that has only `read:content` scope? They should not.
- [ ] **CORS in Production:** Frontend works — but is `allow_origins` locked down to the production domain, not `["*"]`?
- [ ] **Database Migrations:** App starts with correct schema — but does a fresh deploy from scratch run migrations automatically, without manual intervention?
- [ ] **Secrets in Git:** `.env` works locally — but confirm `git ls-files .env` returns nothing.
- [ ] **Async Safety:** Routes feel fast in development — but run a 10-concurrent-request load test to confirm sync ORM isn't blocking the event loop.
- [ ] **MCP Error Handling:** Tools return data correctly — but do they return a structured error (not raise) when the database is unavailable?

---

## Recovery Strategies

| Pitfall | Recovery Cost | Recovery Steps |
|---------|---------------|----------------|
| Secrets committed to git | HIGH | Rotate all exposed credentials immediately in Auth0/DB; use `git filter-repo` to purge history; treat repo as compromised |
| Wrong audience in prod (all 401s) | LOW | Update `AUTH0_AUDIENCE` env var, redeploy; no data loss |
| No migrations in deploy (schema drift) | MEDIUM | Run `alembic upgrade head` manually against prod DB; audit for data loss from missing columns |
| Sync ORM blocking event loop | MEDIUM | Migrate to async SQLAlchemy or switch affected routes to `def`; requires testing all DB handlers |
| MCP routes unprotected in prod | HIGH | Take endpoint offline immediately; audit Auth0 logs for unauthorized access; add auth middleware and redeploy |
| JWKS not cached (rate limited by Auth0) | LOW | Ensure `PyJWKClient` initialized once at startup; redeploy; rate limit clears quickly |

---

## Pitfall-to-Phase Mapping

| Pitfall | Prevention Phase | Verification |
|---------|------------------|--------------|
| Auth0 audience mismatch | Phase 1: Auth foundation | Integration test: foreign-app token returns 401 |
| Auth0 issuer trailing slash | Phase 1: Auth foundation | Integration test: any token decodes without `JWTClaimsError` |
| JWKS not cached | Phase 1: Auth foundation | Confirm `PyJWKClient` instantiated once; load test shows no latency spike |
| CORS wildcard in production | Phase 1: Foundation config | Check `ALLOWED_ORIGINS` env var; verify browser rejects cross-origin request |
| Secrets committed to git | Phase 1: Foundation config | `git ls-files .env` returns empty; CI secret scan passes |
| DB migrations not in deploy | Phase 2: Database setup | Fresh container startup runs migrations automatically; verified in CI |
| Sync ORM blocking event loop | Phase 2: Database setup | 10-concurrent-request load test; latency stays flat |
| FastAPI DI not protecting MCP routes | Phase 3: FastMCP integration | `curl` without token to `/mcp/*` returns 401 |
| MCP tool write scope not checked | Phase 3: FastMCP integration | Read-only token cannot invoke write tools; confirmed by test |
| MCP tool exceptions crash session | Phase 3: FastMCP integration | Trigger DB error mid-tool; verify agent session survives |

---

## Sources

- FastAPI official docs — OAuth2 JWT security tutorial (https://fastapi.tiangolo.com/tutorial/security/oauth2-jwt/) — MEDIUM confidence (fetched 2026-03-25)
- Auth0 JWT validation requirements for RS256 tokens — MEDIUM confidence (training data, Auth0 docs pattern confirmed in practice)
- FastMCP ASGI mounting behavior and dependency injection scope — MEDIUM confidence (training data through August 2025; FastMCP v2.x patterns)
- SQLAlchemy async engine patterns — HIGH confidence (well-established, stable API)
- Auth0 JWKS caching with PyJWT's `PyJWKClient` — MEDIUM confidence (training data + PyJWT docs pattern)
- General FastAPI production deployment gotchas — MEDIUM confidence (training data, community consensus)

**Confidence note:** WebSearch and WebFetch were unavailable during this research session. All findings are from training data (cutoff August 2025) and one successfully fetched FastAPI doc page. Pitfalls related to FastMCP's specific auth integration should be re-verified against current FastMCP docs before implementation.

---
*Pitfalls research for: FastAPI + FastMCP + Auth0 personal portfolio backend*
*Researched: 2026-03-25*
