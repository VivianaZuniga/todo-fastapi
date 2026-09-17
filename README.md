# Todo FastAPI App

A full-stack Todo application built with **FastAPI**, featuring JWT-based authentication, role-based authorization, a SQLAlchemy/PostgreSQL backend, and server-rendered pages with Jinja2 templates.

This project was developed as part of a **FastAPI course** and as personal practice in backend/full-stack web development.

## Features

- User registration and login with **JWT** authentication (OAuth2 password flow).
- Role-based authorization (`admin` vs regular user).
- CRUD operations for personal todos (each user only sees and manages their own todos).
- Admin endpoints to view and delete any user's todos.
- User profile endpoints: view profile, change password, update phone number.
- Server-rendered HTML pages (login, register, todo list, add/edit todo) using Jinja2 and Bootstrap.
- Database schema migrations with Alembic.
- Automated tests with Pytest, running against an isolated SQLite database.
- Containerized setup with Docker and Docker Compose (app + PostgreSQL).

## Tech Stack

- **Backend**: FastAPI, Python 3.10
- **Database**: PostgreSQL (SQLite for automated tests)
- **ORM / Migrations**: SQLAlchemy, Alembic
- **Auth**: OAuth2 password flow + JWT (`python-jose`), password hashing with `passlib`/`bcrypt`
- **Templating**: Jinja2
- **Frontend**: Bootstrap, jQuery (static assets, no JS framework)
- **Testing**: Pytest, FastAPI's `TestClient`
- **Server**: Uvicorn
- **Containerization**: Docker, Docker Compose

## Project Structure

```
TodoApp/
├── main.py                # FastAPI app instance, startup, router registration
├── database.py             # SQLAlchemy engine/session setup
├── models.py                # SQLAlchemy models (Users, Todos)
├── routers/
│   ├── auth.py               # Registration, login/token, get_current_user
│   ├── todos.py               # CRUD for the authenticated user's todos + todo pages
│   ├── admin.py                # Admin-only todo management across all users
│   └── users.py                 # Current user profile, password/phone updates
├── templates/               # Jinja2 HTML templates
├── static/                    # CSS/JS assets (Bootstrap, jQuery)
├── alembic/                     # Database migrations
├── test/                          # Pytest test suite
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── .env.example
```

## Authentication & Authorization

- Users register via `POST /auth/` and log in via `POST /auth/token` (OAuth2 password flow), receiving a JWT access token.
- The JWT payload includes `sub` (username), `id`, and `role`, and is signed with `SECRET_KEY` using HS256.
- API endpoints require a valid `Authorization: Bearer <token>` header (enforced via a FastAPI dependency).
- Server-rendered pages (e.g. the todo list) instead read the `access_token` from a cookie; if it's missing or invalid, the user is redirected to the login page.
- Admin-only endpoints (in `admin.py`) additionally check that the authenticated user has `role == "admin"`.

## Endpoints

### Auth (`/auth`)
| Method | Path | Description |
|---|---|---|
| POST | `/auth/` | Register a new user |
| POST | `/auth/token` | Log in and obtain a JWT access token |
| GET | `/auth/login-page` | Render the login page |
| GET | `/auth/register-page` | Render the registration page |

### Todos (`/todos`)
| Method | Path | Description |
|---|---|---|
| GET | `/todos/` | List the current user's todos |
| GET | `/todos/todo/{todo_id}` | Get a single todo owned by the current user |
| POST | `/todos/todo/` | Create a new todo |
| PUT | `/todos/todo/{todo_id}` | Update a todo owned by the current user |
| DELETE | `/todos/todo/{todo_id}` | Delete a todo owned by the current user |
| GET | `/todos/todo-page` | Render the todo list page |
| GET | `/todos/add-todo-page` | Render the "add todo" page |
| GET | `/todos/edit-todo-page/{todo_id}` | Render the "edit todo" page |

### Admin (`/admin`)
| Method | Path | Description |
|---|---|---|
| GET | `/admin/todos` | List all todos from every user (admin only) |
| DELETE | `/admin/todo/{todo_id}` | Delete any user's todo (admin only) |

### User (`/user`)
| Method | Path | Description |
|---|---|---|
| GET | `/user/` | Get the current user's profile |
| PUT | `/user/password` | Change the current user's password |
| PUT | `/user/phonenumber/` | Update the current user's phone number |

### Misc
| Method | Path | Description |
|---|---|---|
| GET | `/` | Redirects to `/todos/todo-page` |
| GET | `/healthy` | Health check endpoint |

## Database & Models

Two SQLAlchemy models are defined in `models.py`:

- **Users**: `id`, `email`, `username`, `first_name`, `last_name`, `hashed_password`, `is_active`, `role`, `phone_number`
- **Todos**: `id`, `title`, `description`, `priority`, `complete`, `owner_id` (foreign key to `Users.id`)

On startup, `main.py` calls `models.Base.metadata.create_all(bind=engine)` to ensure tables exist. Alembic is used separately for tracked schema migrations.

## Migrations

Schema changes are managed with Alembic (`alembic/`). To generate and apply a migration:

```bash
alembic revision --autogenerate -m "your message"
alembic upgrade head
```

## Templates & Static Files

Server-rendered pages live in `templates/` (`layout.html`, `home.html`, `login.html`, `register.html`, `todo.html`, `add-todo.html`, `edit-todo.html`, `navbar.html`), rendered with Jinja2. Static assets (Bootstrap CSS/JS, jQuery) are served from `static/` at the `/static` path.

## Tests

Tests live in `test/` and use Pytest with FastAPI's `TestClient`. The test suite runs against an isolated SQLite database (`testdb.db`) and overrides the `get_db` and `get_current_user` dependencies, so **no PostgreSQL instance is required** to run them.

Run the full suite from the `TodoApp` directory:

```bash
pytest
```

Run a specific file or test:

```bash
pytest test/test_todos.py
pytest test/test_todos.py::test_create_todo
```

## Environment Variables

Copy `.env.example` to `.env` and fill in your own values:

```bash
cp .env.example .env
```

| Variable | Description |
|---|---|
| `POSTGRES_USER` | PostgreSQL username (used by the `db` container) |
| `POSTGRES_PASSWORD` | PostgreSQL password (used by the `db` container) |
| `POSTGRES_DB` | PostgreSQL database name (used by the `db` container) |
| `DATABASE_URL` | SQLAlchemy connection string used by the app (e.g. `postgresql://user:password@db:5432/dbname`) |
| `SECRET_KEY` | Secret key used to sign JWT tokens |

## Running the Project

### Option 1: Docker Compose (recommended)

This spins up both the PostgreSQL database and the FastAPI app.

```bash
cp .env.example .env   # then edit .env with your own values
docker compose up --build
```

The app will be available at `http://localhost:8000`.

### Option 2: Local development

Requires a running PostgreSQL instance reachable via `DATABASE_URL`.

```bash
pip install -r requirements.txt
cp .env.example .env   # then edit .env with your own values
uvicorn main:app --reload
```

The app will be available at `http://localhost:8000`, with interactive API docs at `http://localhost:8000/docs`.
