---
quick_task: 260328-gez
title: "Blog and Posts API"
one_liner: "Async SQLAlchemy Blog/Post models with full CRUD REST API, Alembic migrations, and 19 passing async tests"
completed_date: "2026-03-28"
duration_minutes: 25
tasks_completed: 8
files_created:
  - server/app/db.py
  - server/app/models/__init__.py
  - server/app/models/blog.py
  - server/app/models/post.py
  - server/alembic.ini
  - server/alembic/env.py
  - server/alembic/versions/0be5f7a0dab5_create_blogs_and_posts_tables.py
  - server/app/controllers/blogs.py
  - server/app/controllers/posts.py
  - server/tests/app/controllers/test_blogs.py
  - server/tests/app/controllers/test_posts.py
  - server/pytest.ini
files_modified:
  - server/main.py
  - server/requirements.txt
key_decisions:
  - Manual alembic migration (no autogenerate) because no live DB available at development time
  - SQLite in-memory via aiosqlite for test isolation without PostgreSQL dependency
  - Dict serialization helpers (_blog_to_response) rather than direct Pydantic ORM serialization for clarity
  - Used List from typing (not list[]) for Python 3.8 compatibility in Docker target environment
---

# Quick Task 260328-gez: Blog and Posts API Summary

**One-liner:** Async SQLAlchemy Blog/Post models with full CRUD REST API, Alembic migrations, and 19 passing async tests

## What Was Built

A complete Blog and Post data layer and REST API for the BigCatTechnologies server:

1. **app/db.py** — Async SQLAlchemy engine, session factory, Base declarative class, and `get_db` FastAPI dependency. Reads DB_HOST, DB_NAME, DB_USER, DB_PASSWORD from environment.

2. **app/models/blog.py + post.py** — SQLAlchemy ORM models for Blog (id, name, description, timestamps) and Post (id, blog_id FK, title, body, timestamps) with a one-to-many relationship.

3. **alembic/** — Alembic initialized with async engine configuration in env.py. Initial migration creates blogs and posts tables with a blog_id index.

4. **app/controllers/blogs.py** — Four routes: POST /blogs, GET /blogs, GET /blogs/{id} (with posts), PATCH /blogs/{id}.

5. **app/controllers/posts.py** — One route: POST /blogs/{blog_id}/posts.

6. **main.py** — Both controllers wired with `register()` calls.

7. **tests/** — 14 new async tests for blogs and posts (+ 5 existing health tests = 19 total passing).

8. **pytest.ini** — asyncio_mode=auto for seamless async test execution.

## Test Results

```
19 passed in 0.54s
```

All tests pass including pre-existing health tests.

## Deviations from Plan

**1. [Rule 1 - Bug] Python 3.8 list type hint compatibility**
- **Found during:** Task 3 (models)
- **Issue:** `Mapped[list["Post"]]` syntax requires Python 3.9+; local environment is Python 3.8
- **Fix:** Used `from typing import List` and `Mapped[List["Post"]]`
- **Files modified:** server/app/models/blog.py
- **Commit:** 72c2fa2

**2. [Rule 3 - Blocking] No pytest config existed**
- **Found during:** Task 8 (tests)
- **Issue:** `asyncio_mode = "auto"` required for async fixture support but no pytest.ini existed
- **Fix:** Created server/pytest.ini with asyncio_mode=auto and testpaths=tests
- **Files modified:** server/pytest.ini (created)
- **Commit:** 897e833

**3. Manual alembic migration instead of autogenerate**
- **Found during:** Task 4 (alembic)
- **Issue:** `alembic revision --autogenerate` requires an active DB connection; no live PostgreSQL available
- **Fix:** Created migration manually with explicit `op.create_table()` calls — functionally identical outcome
- **No behavior change for production** — migration file is correct

## Known Stubs

None — all endpoints are fully wired to the async database session.

## Self-Check: PASSED

Files exist:
- server/app/db.py: FOUND
- server/app/models/blog.py: FOUND
- server/app/models/post.py: FOUND
- server/alembic/env.py: FOUND
- server/alembic/versions/0be5f7a0dab5_create_blogs_and_posts_tables.py: FOUND
- server/app/controllers/blogs.py: FOUND
- server/app/controllers/posts.py: FOUND
- server/tests/app/controllers/test_blogs.py: FOUND
- server/tests/app/controllers/test_posts.py: FOUND
- server/pytest.ini: FOUND

Commits:
- a18adcd: chore(260328-gez): add sqlalchemy, asyncpg, alembic, aiosqlite to requirements
- 08ab63b: feat(260328-gez): add async SQLAlchemy db setup with Base and session factory
- 72c2fa2: feat(260328-gez): add Blog and Post SQLAlchemy models
- 5a798e6: feat(260328-gez): init alembic with async engine and initial blog/post migration
- a60640b: feat(260328-gez): add blogs and posts controllers
- 1dfb0d4: feat(260328-gez): wire blogs and posts controllers in main.py
- 897e833: test(260328-gez): add tests for blogs and posts controllers
