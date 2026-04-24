# BigCatTechnologies — Project Context

## What It Is

A personal hub and self-advertisement platform for Sam Shapiro at **https://bigcattechnologies.com**.

The backend doubles as an MCP server so AI agents (Claude, Cursor, etc.) can query the site's content and eventually trigger actions on personal projects. Public REST API for the frontend; authenticated MCP interface for agents.

---

## URLs

| Service | URL |
|---------|-----|
| Site | https://bigcattechnologies.com |
| API | https://api.bigcattechnologies.com |
| MCP endpoint | https://api.bigcattechnologies.com/mcp |

---

## Repo Layout

```
BigCatTechnologies/
├── server/         # FastAPI + FastMCP backend (Python)
├── client/         # React + TypeScript + Vite frontend
├── terraform/      # Infrastructure-as-code
└── docker-compose.yml
```

---

## Stack

### Server (Python)
| Layer | Tech |
|-------|------|
| Framework | FastAPI 0.115.x |
| MCP | FastMCP 2.x (mounted at `/mcp`) |
| ORM | SQLAlchemy 2.x async |
| DB | PostgreSQL 16 |
| Driver | asyncpg |
| Migrations | Alembic |
| Auth | Auth0 SSO (JWT validation via python-jose) |
| Config | pydantic-settings |
| Server | Uvicorn |
| Package mgr | uv |

### Client (TypeScript)
| Layer | Tech |
|-------|------|
| Framework | React 19 + TypeScript |
| Build | Vite |
| UI | MUI v7 + Toolpad Core |
| Auth | @auth0/auth0-react |
| Routing | react-router-dom v7 |
| Editor | EasyMDE (markdown) |
| Testing | Vitest + Testing Library |

### Infrastructure
- Docker + docker-compose (local dev parity)
- Terraform (infra provisioning)
- GitHub Actions (CI: tests + Docker builds)

---

## Architecture

- Single ASGI process: FastAPI REST + FastMCP mounted at `/mcp`
- Auth0 bearer token required on MCP routes and admin REST routes
- Public read endpoints (blog posts, projects, resume) unauthenticated
- No custom auth — Auth0 SSO only

### FastMCP Mount Pattern
```python
from fastapi import FastAPI
from fastmcp import FastMCP

app = FastAPI()
mcp = FastMCP("BigCatTechnologies")

app.mount("/mcp", mcp.get_asgi_app())
```
⚠️ FastAPI `Depends()` does NOT protect mounted ASGI sub-apps — auth must be enforced at ASGI middleware or OAuthProxy layer.

---

## Blog

| Blog | ID |
|------|----|
| Mox's Blog | `d269d2a7-eecd-4cbf-b6e5-a48025933c7f` |
| Sam's Blog | `9c151615-550b-4da9-8cc3-6bd06048118d` |

**Create a post:** `mcporter call bigcat.create_post_in_blog` (creates as draft)  
**MCP server name:** `bigcat` (registered in mcporter)  
**Draft blog posts:** `~/.openclaw/workspace/blog/`

---

## Current Status

**Phase: 1 — Scaffold** (in progress)
- Phase goal: Docker runs, secrets from env, `/health` endpoint
- Phase 2 goal: Authenticated MCP endpoint (`/mcp`) that agents can connect to

### Completed Work
| Date | Task |
|------|------|
| 2026-03-28 | Quick task: Blog + Post models with full CRUD API (commit `093be07`) |

### Next Steps
- Execute Phase 1 scaffold (docker-compose, secrets, /health)
- Then Phase 2: Auth0 + OAuthProxy + MCP hello_world tool

---

## Key Decisions

| Decision | Rationale |
|----------|-----------|
| FastAPI + FastMCP | User preference; single process serves HTTP + MCP |
| Auth0 SSO | No custom auth; OAuth2/JWT |
| PostgreSQL | Production ACID, concurrent writes; SQLite for local only |
| uv | Faster than pip/poetry; becoming community standard |
| Auth on MCP via ASGI middleware | FastAPI Depends() doesn't reach mounted sub-apps |

---

## Known Risks / Blockers

- FastMCP v2 exact auth hook API should be verified at https://gofastmcp.com before Phase 2 implementation (training data is Aug 2025)

---

## Planning Docs (server)

Detailed planning files live in `server/.planning/`:
- `PROJECT.md` — requirements and decisions
- `ROADMAP.md` — phases and success criteria
- `STATE.md` — current position and session continuity
- `research/` — stack research, architecture, features, pitfalls

---

*Last updated: 2026-04-15*
