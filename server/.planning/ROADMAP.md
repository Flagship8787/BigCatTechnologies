# Roadmap: BigCatTechnologies Server

## Overview

Two phases deliver the v1 milestone: a safe, runnable project scaffold followed by a working authenticated MCP endpoint. Phase 1 eliminates all catastrophic foundation mistakes (secrets in git, CORS wildcards, missing health checks) before any feature code is written. Phase 2 wires Auth0 + OAuthProxy + FastMCP together and proves an AI agent can connect and invoke a tool through an authenticated endpoint. All v2 content features (blog, projects, resume, full MCP interface) are deferred — v1 validates the architecture, not the content.

## Phases

**Phase Numbering:**
- Integer phases (1, 2, 3): Planned milestone work
- Decimal phases (2.1, 2.2): Urgent insertions (marked with INSERTED)

Decimal phases appear between their surrounding integers in numeric order.

- [ ] **Phase 1: Scaffold** - Safe, runnable project foundation with Docker, secrets management, and health endpoint
- [ ] **Phase 2: Auth + MCP** - Authenticated MCP endpoint that an AI agent can connect to and invoke a tool through

## Phase Details

### Phase 1: Scaffold
**Goal**: The project runs in Docker with all secrets from environment variables, no credentials in git, and a health endpoint confirming the service is alive
**Depends on**: Nothing (first phase)
**Requirements**: INFRA-01, INFRA-02, INFRA-03, INFRA-04, INFRA-05, INFRA-06
**Success Criteria** (what must be TRUE):
  1. `docker-compose up` starts the FastAPI service and PostgreSQL without errors
  2. `GET /health` returns HTTP 200 with a service status payload
  3. `.env` is absent from git history; `.env.example` lists every required key with placeholder values
  4. CORS allowed origins are read from an environment variable, not hardcoded in source
  5. All secrets (database URL, Auth0 credentials, CORS origins) are loaded via pydantic-settings with no hardcoded fallbacks
**Plans**: TBD

### Phase 2: Auth + MCP
**Goal**: An AI agent can connect to the MCP server at `/mcp`, invoke the `hello_world` tool, and unauthenticated requests are rejected with 401
**Depends on**: Phase 1
**Requirements**: AUTH-01, AUTH-02, AUTH-03, MCP-01, MCP-02, MCP-03, MCP-04
**Success Criteria** (what must be TRUE):
  1. An AI agent (e.g. Claude) connects to `/mcp` with a valid Auth0 session and successfully invokes the `hello_world` tool, receiving a greeting string
  2. A `curl` request to `/mcp` without an Authorization header returns HTTP 401
  3. A `curl` request to `/mcp` with an invalid or expired token returns HTTP 401
  4. Auth0 tenant, OAuthProxy configuration, and all required environment keys are documented in `.env.example`
**Plans**: TBD
**UI hint**: no

## Progress

**Execution Order:**
Phases execute in numeric order: 1 → 2

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 1. Scaffold | 0/? | Not started | - |
| 2. Auth + MCP | 0/? | Not started | - |
