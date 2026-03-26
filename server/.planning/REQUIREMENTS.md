# Requirements: BigCatTechnologies Server

**Defined:** 2026-03-25
**Core Value:** A single authenticated backend that powers both the public-facing website and an MCP interface for AI agents to discover and interact with the owner's projects.

## v1 Requirements

### Infrastructure

- [ ] **INFRA-01**: Project scaffold exists with uv, pyproject.toml, and all dependencies pinned
- [ ] **INFRA-02**: Application runs in Docker with docker-compose (FastAPI + PostgreSQL services)
- [ ] **INFRA-03**: All secrets loaded from environment variables via pydantic-settings (no hardcoded values)
- [ ] **INFRA-04**: `.env` is excluded from git; `.env.example` exists with all required keys
- [ ] **INFRA-05**: CORS configured via environment variable (not hardcoded wildcard)
- [ ] **INFRA-06**: Health endpoint (`GET /health`) returns 200 with service status

### Auth

- [ ] **AUTH-01**: OAuthProxy sits in front of the `/mcp` path and gates access via Auth0
- [ ] **AUTH-02**: Unauthenticated requests to protected routes return 401
- [ ] **AUTH-03**: Auth0 tenant and OAuthProxy configured and documented in `.env.example`

### MCP

- [ ] **MCP-01**: FastMCP server mounted at `/mcp` within the FastAPI application
- [ ] **MCP-02**: MCP server exposes a `hello_world` tool that returns a greeting string
- [ ] **MCP-03**: An AI agent (e.g. Claude) can connect to the MCP server and invoke the `hello_world` tool successfully
- [ ] **MCP-04**: MCP server is unreachable without valid Auth0 session (OAuthProxy enforces this)

## v2 Requirements

### Blog

- **BLOG-01**: User can create blog posts with title, body, and slug
- **BLOG-02**: User can tag blog posts
- **BLOG-03**: Public can read published blog posts
- **BLOG-04**: Admin can update and delete blog posts
- **BLOG-05**: Posts support draft/published status

### Projects

- **PROJ-01**: Admin can add/edit/remove project entries
- **PROJ-02**: Projects can be tagged by tech stack
- **PROJ-03**: Projects include links (repo, demo)
- **PROJ-04**: Public can browse project showcase

### Resume

- **RESU-01**: Public can fetch structured resume data (JSON Resume schema)
- **RESU-02**: Admin can update resume via authenticated API

### MCP Content Interface

- **MCPC-01**: MCP resources expose blog posts, projects, resume to agents
- **MCPC-02**: MCP read-only tools allow agents to query content
- **MCPC-03**: MCP prompts provide canned agent workflows (summarize work, find projects by tech)
- **MCPC-04**: Auth-gated MCP write tools allow agents to create draft blog posts

## Out of Scope

| Feature | Reason |
|---------|--------|
| Visitor accounts / user registration | Single-owner site — only owner auth needed |
| Comments system | Not a community platform; deferred indefinitely |
| Real-time features (WebSockets) | No use case in v1 or v2 |
| File/media upload API | Unnecessary complexity for a portfolio site |
| Full-text search engine | PostgreSQL FTS sufficient if needed later |
| Multi-user admin | Single owner only |
| MCP sampling | Out of scope for this server's role |

## Traceability

| Requirement | Phase | Status |
|-------------|-------|--------|
| INFRA-01 | Phase 1 | Pending |
| INFRA-02 | Phase 1 | Pending |
| INFRA-03 | Phase 1 | Pending |
| INFRA-04 | Phase 1 | Pending |
| INFRA-05 | Phase 1 | Pending |
| INFRA-06 | Phase 1 | Pending |
| AUTH-01 | Phase 2 | Pending |
| AUTH-02 | Phase 2 | Pending |
| AUTH-03 | Phase 2 | Pending |
| MCP-01 | Phase 2 | Pending |
| MCP-02 | Phase 2 | Pending |
| MCP-03 | Phase 2 | Pending |
| MCP-04 | Phase 2 | Pending |

**Coverage:**
- v1 requirements: 13 total
- Mapped to phases: 13
- Unmapped: 0 ✓

---
*Requirements defined: 2026-03-25*
*Last updated: 2026-03-25 after initial definition*
