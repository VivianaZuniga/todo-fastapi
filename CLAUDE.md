# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project overview

A FastAPI Todo application with JWT-based auth, server-rendered Jinja2 pages, and a SQLAlchemy/PostgreSQL backend (SQLite for tests). Originally built as part of a FastAPI course.

## Environment setup

Requires a `.env` file (gitignored) with:
- `DATABASE_URL` — SQLAlchemy connection string (e.g. `postgresql://vivi:vivi@localhost:5433/my_database`)
- `SECRET_KEY` — JWT signing secret

## Common commands

Run the app locally (requires Postgres running, see `docker-compose.yml` for local db creds):
```
uvicorn main:app --reload
```

Run the full stack (Postgres + app) via Docker:
```
docker-compose up --build
```

Run tests (uses an isolated SQLite file `testdb.db`, no Postgres needed):
```
pytest
pytest test/test_todos.py            # single file
pytest test/test_todos.py::test_create_todo   # single test
```

Database migrations (Alembic, configured against `DATABASE_URL` via `alembic/env.py`):
```
alembic revision --autogenerate -m "message"
alembic upgrade head
```

## Architecture

**Entry point**: [main.py](main.py) creates the `FastAPI` app, calls `models.Base.metadata.create_all(bind=engine)` to sync tables on startup (no migration gating — Alembic is used separately for schema changes), mounts `/static`, and includes all routers.

**Routers** (`routers/`), each an `APIRouter` with its own prefix, all following the same shape — Pydantic request models, a `user_dependency`/`db_dependency` pair injected per-route, manual `if user is None` auth checks, and a `#Pages` vs `#Endpoints` section split within the file:
- `auth.py` — user registration, JWT login/token issuance, and `get_current_user` (decodes the bearer token / cookie into `{'username', 'id', 'role'}`). This is the shared auth dependency imported by every other router.
- `todos.py` — CRUD for the authenticated user's todos, plus the server-rendered `/todos/todo-page`.
- `admin.py` — todo CRUD across all users, gated by `user.get('role') != 'admin'` checks.
- `users.py` — current user profile, password change, phone number change.

**Auth model**: JWT (`python-jose`, HS256) via OAuth2 password flow (`/auth/token`). Page routes (e.g. `todo-page`) authenticate by reading the `access_token` cookie directly and calling `get_current_user` manually (not via `Depends`), since browsers hitting HTML pages don't send an `Authorization` header. On failure they redirect to `/auth/login-page` and clear the cookie (`redirect_to_login()` in `todos.py`). API routes instead use `user_dependency = Annotated[dict, Depends(get_current_user)]`, which raises 401 automatically for a missing/invalid `Authorization: Bearer` token.

**Database layer** ([database.py](database.py)): single `engine`/`SessionLocal` built from `DATABASE_URL`. `get_db()` is the FastAPI dependency yielding a session per-request; `db_dependency = Annotated[Session, Depends(get_db)]` is imported by every router. Models live in [models.py](models.py) (`Users`, `Todos`, with `Todos.owner_id` FK to `Users.id`).

**Templates** ([templates/](templates/)): Jinja2 pages (`layout.html` base, `home.html`, `login.html`, `register.html`, `todo.html`) rendered via `Jinja2Templates(directory="templates")`, instantiated separately in `main.py` and in each router that serves pages. Static assets (Bootstrap, jQuery) are in [static/](static/), served at `/static`.

**Tests** (`test/`): `test/utils.py` is the shared fixture module — it builds a separate SQLite engine/session, overrides `get_db` and `get_current_user` via `app.dependency_overrides`, and provides `test_todo`/`test_user` pytest fixtures that insert a row and clean up the table afterward via raw `DELETE`. Each `test_*.py` file re-applies the dependency overrides at import time (`app.dependency_overrides[...] = ...`) and does `from .utils import *`. New tests for a router should follow this same override + fixture pattern rather than hitting a real Postgres db.
