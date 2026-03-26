# Feature Research

**Domain:** Personal portfolio/hub backend with MCP server integration
**Researched:** 2026-03-25
**Confidence:** MEDIUM (no live web access; based on MCP spec knowledge, FastMCP training data through Aug 2025, and personal portfolio backend patterns)

---

## Feature Landscape

### Table Stakes (Users Expect These)

"Users" here means two audiences: (1) human visitors via a frontend, and (2) AI agents connecting via MCP. Both audiences have non-negotiable expectations.

| Feature | Why Expected | Complexity | Notes |
|---------|--------------|------------|-------|
| Public blog post listing | Any portfolio site serves blog content; GET /posts is baseline | LOW | Pagination, filtering by tag/date |
| Public blog post detail | Individual post by slug or ID; SEO requires stable URLs | LOW | Slug-based routing preferred |
| Public project listing | Core purpose of portfolio — show what you've built | LOW | Fields: name, description, links, tech tags, status |
| Public project detail | Per-project deep dive page | LOW | Consistent with post detail pattern |
| Public resume endpoint | Structured resume data for frontend rendering or agent consumption | LOW | JSON schema matters; drives multiple consumers |
| Admin CRUD: blog posts | Owner must be able to create/edit/delete posts | MEDIUM | Requires Auth0 JWT middleware on write routes |
| Admin CRUD: projects | Owner must be able to manage project entries | MEDIUM | Same auth pattern as blog admin |
| Admin CRUD: resume | Owner must be able to update resume data | LOW | Single-resource pattern (no listing needed) |
| Auth0 JWT verification | Protected routes need verified identity | MEDIUM | FastAPI dependency injection; verify RS256 JWT from Auth0 JWKS endpoint |
| Health/liveness endpoint | Deployment infrastructure requires it | LOW | GET /health → 200 OK |
| MCP server mount | Agents expect an MCP-reachable server; this is the core differentiator baseline | MEDIUM | FastMCP mounted on FastAPI via streamable-HTTP or SSE transport |
| MCP resource: blog posts | Agents expect to read blog content as MCP resources | LOW | URI pattern: `blog://posts`, `blog://posts/{slug}` |
| MCP resource: projects | Agents expect to read project list/detail | LOW | URI pattern: `projects://list`, `projects://{id}` |
| MCP resource: resume | Agents expect to read resume data | LOW | URI pattern: `resume://current` |

### Differentiators (Competitive Advantage)

These features move the backend beyond "yet another portfolio API" and fulfill the stated core value: a backend that AI agents can meaningfully interact with.

| Feature | Value Proposition | Complexity | Notes |
|---------|-------------------|------------|-------|
| MCP tools: project actions | Agents can trigger actions on personal projects (e.g., run a demo, get status, ping a service) — goes beyond read-only | HIGH | Each project integration is bespoke; extensibility pattern matters more than initial depth |
| MCP prompts: canned agent prompts | FastMCP supports prompt primitives; pre-packaged prompts (e.g., "Summarize my recent work", "What projects use Python?") make agent workflows reusable | MEDIUM | Prompts are first-class MCP primitives; under-utilized in most implementations |
| MCP tool: search/filter content | Agents can query "find posts about Kubernetes" rather than listing all then filtering client-side | MEDIUM | Server-side search avoids agent doing N+1 resource reads |
| Auth-gated MCP tools | Write-capable MCP tools (e.g., create draft post) protected by same Auth0 JWT — lets owner use agents as admin interface | HIGH | Requires MCP transport to forward Authorization header; verify on tool invocation |
| Structured resume schema | Resume data modeled as JSON Resume spec (jsonresume.org schema) — widely understood by frontends and agents alike | LOW | Adopt existing schema rather than inventing; reduces agent confusion |
| Blog post tags/categories | Enables filtering and agent queries like "show me DevOps posts" | LOW | Many portfolios skip this; adds nav value |
| Project tech tags | Enables agent queries like "what projects use FastAPI?" — critical for MCP usefulness | LOW | Simple string array per project; no separate tag entity needed |
| OpenAPI docs served publicly | Downstream frontend devs and agent builders can explore the API without asking owner | LOW | FastAPI auto-generates; just ensure it's not disabled in prod |
| Extensible project integration registry | Pattern for registering per-project MCP tool handlers so new projects can be onboarded without restructuring | HIGH | This is architectural but manifests as a feature: "adding project X gives agents access to it automatically" |

### Anti-Features (Commonly Requested, Often Problematic)

| Feature | Why Requested | Why Problematic | Alternative |
|---------|---------------|-----------------|-------------|
| Visitor user accounts / registration | "Let visitors follow the blog" | Massive scope increase: auth flows, account management, email verification, GDPR concerns — for a personal site with one owner this is disproportionate | RSS feed or newsletter link in resume data |
| Comments system | Standard blog feature | Moderation overhead, spam surface, another storage domain; Auth0 is owner-only so no visitor identity exists | Link to GitHub Discussions or Twitter/X thread per post |
| Real-time features (WebSockets) | "Live project status dashboard" | Operational complexity with no clear user value for a portfolio; MCP transports already use SSE for streaming where needed | Polling endpoint for project status; MCP tool returns current status on demand |
| File/media upload API | "Let me upload images for posts" | Binary storage, CDN config, content-type validation, size limits — complexity that serves a single user | Reference external image URLs (Cloudinary, S3 presigned); store URL string in post body |
| Full-text search engine (Elasticsearch/Algolia) | "Search the blog" | Operational overhead for a personal site with likely <500 posts ever | PostgreSQL full-text search (tsvector) or simple ILIKE for this scale |
| Multi-user admin / roles | "What if a collaborator wants to post?" | Scope creep; Auth0 SSO is configured for single owner | If needed later, Auth0 roles/permissions can be added — but don't design for it now |
| Versioned blog post history | "Track edits like a wiki" | Schema complexity, storage growth, no clear consumer on a personal site | Store `updated_at` timestamp; that's sufficient |
| MCP sampling (LLM calls from server) | "Server initiates LLM calls back to the agent" | MCP sampling is the reverse direction (server asks client to run LLM); adds bidirectional complexity and is rarely needed | Use MCP tools/resources for agent-initiated flows; server stays stateless |

---

## Feature Dependencies

```
Auth0 JWT Verification
    └──required by──> Admin CRUD: blog posts
    └──required by──> Admin CRUD: projects
    └──required by──> Admin CRUD: resume
    └──required by──> Auth-gated MCP tools (write operations)

Database (PostgreSQL)
    └──required by──> Blog post CRUD (all)
    └──required by──> Project CRUD (all)
    └──required by──> Resume storage
    └──required by──> Blog post tags
    └──required by──> Project tech tags

Public read endpoints
    └──required by──> MCP resources (resources delegate to same service layer)
    └──required by──> MCP search tool

MCP server mount (FastMCP on FastAPI)
    └──required by──> MCP resources: blog posts
    └──required by──> MCP resources: projects
    └──required by──> MCP resources: resume
    └──required by──> MCP tools: search/filter
    └──required by──> MCP tools: project actions
    └──required by──> MCP prompts: canned prompts

Project tech tags ──enhances──> MCP tool: search/filter content
Blog post tags    ──enhances──> MCP tool: search/filter content

Extensible project integration registry ──enables──> MCP tools: project actions
    (registry pattern must exist before per-project integrations are added)
```

### Dependency Notes

- **Auth0 JWT verification requires nothing internal** but must be in place before any protected route or tool is implemented; it is a cross-cutting concern established in the foundation phase.
- **MCP resources delegate to the same service layer as HTTP endpoints** — this is a strength: no duplicate data access logic. MCP resources are thin wrappers over the same blog/project/resume service functions.
- **Project integration registry requires upfront architectural decision** — even if zero integrations exist at launch, the pattern (how a new project registers its MCP tools) must be defined early to avoid structural rewrites when the first real integration arrives.
- **Tags (blog and project) enhance MCP search** — without tags, search is limited to text matching on title/body. Tags make agent queries dramatically more precise and are low effort to add early.

---

## MVP Definition

### Launch With (v1)

Minimum viable product — enough to have a working portfolio + working MCP interface.

- [ ] Database models for posts, projects, resume — foundation everything else builds on
- [ ] Public read API: GET /posts, GET /posts/{slug}, GET /projects, GET /projects/{id}, GET /resume — human visitors can access all content
- [ ] Admin write API: POST/PUT/DELETE for posts, projects, resume — owner can manage content
- [ ] Auth0 JWT verification middleware — gates admin routes
- [ ] MCP server mounted on FastAPI — agents can connect
- [ ] MCP resources: blog posts, projects, resume — agents can read content
- [ ] Health endpoint — deployment infrastructure requires it
- [ ] Blog post tags + project tech tags — enables meaningful agent queries from day one

### Add After Validation (v1.x)

Features to add once core is working and the MCP interface proves useful.

- [ ] MCP tool: search/filter content — add when agent interactions reveal the need to query rather than list
- [ ] MCP prompts: canned prompts — add when common agent workflows emerge from real usage
- [ ] Auth-gated MCP write tools — add when owner wants to use agents as admin interface (create draft via agent)
- [ ] Structured resume (JSON Resume schema) — refine schema after initial version validates fields needed

### Future Consideration (v2+)

Features to defer until extensibility is needed.

- [ ] MCP tools: project actions (per-project integrations) — defer until a specific project warrants agent interaction; design the registry pattern in v1.x, implement first real integration in v2
- [ ] Extensible project integration registry — formal registry pattern; needed before second project integration but not for first
- [ ] RSS feed endpoint — low value until there's readership; trivial to add later

---

## Feature Prioritization Matrix

| Feature | User Value | Implementation Cost | Priority |
|---------|------------|---------------------|----------|
| Public read API (posts, projects, resume) | HIGH | LOW | P1 |
| Admin CRUD (posts, projects, resume) | HIGH | MEDIUM | P1 |
| Auth0 JWT verification | HIGH | MEDIUM | P1 |
| MCP server mount | HIGH | MEDIUM | P1 |
| MCP resources (blog, projects, resume) | HIGH | LOW | P1 |
| Health endpoint | HIGH | LOW | P1 |
| Blog post tags + project tech tags | MEDIUM | LOW | P1 |
| OpenAPI docs (auto via FastAPI) | MEDIUM | LOW | P1 |
| MCP tool: search/filter | MEDIUM | MEDIUM | P2 |
| MCP prompts: canned prompts | MEDIUM | LOW | P2 |
| Auth-gated MCP write tools | MEDIUM | HIGH | P2 |
| Structured resume (JSON Resume schema) | MEDIUM | LOW | P2 |
| MCP tools: project actions | HIGH (eventual) | HIGH | P3 |
| Extensible project integration registry | HIGH (eventual) | HIGH | P3 |
| RSS feed | LOW | LOW | P3 |

**Priority key:**
- P1: Must have for launch
- P2: Should have, add when possible
- P3: Nice to have, future consideration

---

## MCP-Specific Feature Detail

MCP has three first-class server primitives. This project uses all three:

### Resources (read-only, URI-addressed content)

Resources are the MCP equivalent of GET endpoints. Agents read them to understand context.

| Resource URI Pattern | Content | Notes |
|---------------------|---------|-------|
| `blog://posts` | List of all posts (title, slug, tags, date, excerpt) | Paginated or capped at reasonable limit |
| `blog://posts/{slug}` | Full post content | Markdown body + metadata |
| `projects://list` | All projects | Name, description, tech tags, links, status |
| `projects://{id}` | Single project detail | Full record |
| `resume://current` | Full resume data | JSON Resume schema recommended |

Resources are **read-only and owner-auth-free** — they mirror the public HTTP read API. FastMCP uses `@mcp.resource()` decorator.

### Tools (executable functions, can have side effects)

Tools are the MCP equivalent of POST/action endpoints. Agents call them to do things.

| Tool Name | Action | Auth Required | Notes |
|-----------|--------|---------------|-------|
| `search_content` | Full-text + tag search across posts and projects | No | Returns matched items with type label |
| `create_draft_post` | Creates a draft blog post | Yes (owner JWT) | Auth-gated write tool; enables agent-as-admin-interface |
| `get_project_status` | Calls a specific project's status endpoint | No | First real project action integration |
| `trigger_project_action` | Sends a command to a specific registered project | Yes (owner JWT) | Extensible; registry pattern governs which projects expose which actions |

Tools use `@mcp.tool()` decorator in FastMCP. Auth-gated tools must inspect the MCP request context for a forwarded Authorization header — this is a non-trivial integration point.

### Prompts (parameterized prompt templates)

Prompts are reusable templates agents can invoke to get a structured starting prompt for a task.

| Prompt Name | Purpose | Parameters | Notes |
|-------------|---------|------------|-------|
| `summarize_recent_work` | "What have I been up to lately?" starting prompt | `since_date` (optional) | Useful for generating bio updates, LinkedIn summaries |
| `find_projects_by_tech` | "What projects use X?" structured query | `tech_stack` | Guides agent to use the right resources |
| `draft_blog_post` | Scaffolds a post draft based on topic | `topic`, `tone` | Owner uses with Claude to generate post starters |

Prompts use `@mcp.prompt()` decorator. They are low-cost to implement and make the server significantly more useful to agents.

---

## Competitor Feature Analysis

Personal portfolio backends are rarely open-sourced in a comparable way, but the patterns are well-established:

| Feature | Typical Portfolio (no MCP) | Ghost/Headless CMS | This Project |
|---------|---------------------------|-------------------|--------------|
| Blog CRUD | Via CMS UI | Yes | API-first, owner via HTTP or agent |
| Projects showcase | Static data or CMS | Workaround | First-class entity with tech tags |
| Resume | Static file | N/A | Structured JSON endpoint |
| Agent access | None | None | MCP resources + tools + prompts |
| Auth | None (public) or full user auth | Multi-user CMS auth | Auth0 SSO, owner-only |
| Project actions | None | None | Extensible MCP tools (unique) |

The MCP interface is the genuine differentiator. No mainstream portfolio solution exposes content as MCP resources or enables agents to trigger project actions.

---

## Sources

- MCP specification knowledge (tools, resources, prompts primitives) — training data through Aug 2025, HIGH confidence on primitives
- FastMCP library patterns (`@mcp.tool`, `@mcp.resource`, `@mcp.prompt` decorators) — MEDIUM confidence; verify against current FastMCP docs at gofastmcp.com
- Auth0 FastAPI JWT integration pattern (JWKS RS256 verification via `python-jose` or `authlib`) — MEDIUM confidence; standard pattern unlikely to have changed
- JSON Resume schema (jsonresume.org) — LOW confidence on current version; verify schema fields before adopting
- Personal portfolio backend conventions — HIGH confidence; stable domain

---

*Feature research for: BigCatTechLab Server (FastAPI + FastMCP personal portfolio/hub backend)*
*Researched: 2026-03-25*
