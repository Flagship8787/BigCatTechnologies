# BigCatTechnologies Server

## What This Is

A FastAPI + FastMCP backend for bigcattechnologies.com — a personal hub and self-advertisement platform. It serves a portfolio of personal projects, a resume, and a blog, while also exposing an MCP interface so AI agents can read site content and interact with personal projects.

## Core Value

A single authenticated backend that powers both the public-facing website and an MCP interface for AI agents to discover and interact with the owner's projects.

## Requirements

### Validated

(None yet — ship to validate)

### Active

- [ ] Blog with database-backed posts (create, read, update, delete)
- [ ] Project showcase with links and descriptions
- [ ] Resume endpoint serving structured resume data
- [ ] Auth0 SSO authentication for admin/protected routes
- [ ] FastMCP interface exposing content (blog, projects, resume) to AI agents
- [ ] FastMCP interface enabling agents to trigger actions on personal projects
- [ ] Public read API for site content (blog posts, projects, resume)
- [ ] Admin-protected write API for managing content

### Out of Scope

- User accounts for site visitors — only owner auth (Admin0 SSO for owner only)
- Comments/discussion system — not needed for v1
- Frontend/UI — this is a backend only; frontend is a separate concern

## Context

- Hosted at bigcattechnologies.com
- The MCP integration (FastMCP) is a key differentiator — the backend doubles as an MCP server so agents (e.g., Claude, Cursor) can query projects, read blog posts, and eventually trigger project actions
- Personal projects vary in type (web services, scripts, hardware/IoT) — the MCP interface should be extensible as new projects are added
- Auth0 for SSO means no custom auth implementation needed; integration via OAuth2/JWT

## Constraints

- **Tech Stack**: Python, FastAPI, FastMCP — established by user preference
- **Auth**: Auth0 SSO only — no custom auth system
- **Deployment**: Must be hostable at bigcattechnologies.com (likely containerized or VPS)

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| FastAPI + FastMCP | User preference; FastMCP enables MCP protocol natively in FastAPI | — Pending |
| Auth0 for SSO | Avoid building/maintaining custom auth; SSO is more secure | — Pending |
| Database-backed blog | Allows dynamic content management via API | — Pending |

## Evolution

This document evolves at phase transitions and milestone boundaries.

**After each phase transition** (via `/gsd:transition`):
1. Requirements invalidated? → Move to Out of Scope with reason
2. Requirements validated? → Move to Validated with phase reference
3. New requirements emerged? → Add to Active
4. Decisions to log? → Add to Key Decisions
5. "What This Is" still accurate? → Update if drifted

**After each milestone** (via `/gsd:complete-milestone`):
1. Full review of all sections
2. Core Value check — still the right priority?
3. Audit Out of Scope — reasons still valid?
4. Update Context with current state

---
*Last updated: 2026-03-25 after initialization*
