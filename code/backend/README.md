# backend

FastAPI service. One process exposes:

- **Management API** (`/api/…`) — used by Studio; session-cookie auth. OpenAPI docs at
  `/api/docs`.
- **SDK API** (`/sdk/v1/…`, from M1) — used by the browser SDK.
- **Static files** — the built Studio at `/` (when `STUDIO_DIST` is set) and, from M1, `/sdk.js`.

| Path | What |
|---|---|
| `app/main.py` | `create_app()` factory, health check, CSRF origin check, Studio mount |
| `app/config.py` | Settings from environment variables |
| `app/auth.py` | First-run setup, sign-in, sessions |
| `app/models.py` | SQLAlchemy models |
| `migrations/` | Alembic migrations — never edit one that has been released |
| `tests/` | pytest, against a real Postgres |

## Develop

Needs [uv](https://docs.astral.sh/uv/) and the local emulators (`scripts/dev-services.sh up`).
Defaults in `app/config.py` already point at them.

```bash
uv sync                                   # create .venv with all dependencies
uv run alembic upgrade head               # migrate the dev database
uv run uvicorn app.main:create_app --factory --reload --port 8000
```

Then run Studio's dev server (`code/studio`), which proxies `/api` here, and open
http://localhost:5173.

## Check

```bash
uv run ruff format .        # format (CI runs: ruff format --check .)
uv run ruff check .         # lint
uv run mypy                 # types (strict)
uv run pytest               # all tests; needs the Postgres emulator
uv run pytest tests/test_auth.py::test_login_and_logout   # one test
```

Tests recreate and migrate a `guide_test` database once per run. Point them elsewhere with
`TEST_DATABASE_URL`.

## Migrations

```bash
uv run alembic revision -m "add experiences"   # then edit migrations/versions/<rev>_*.py
uv run alembic upgrade head
```

The Docker image runs `alembic upgrade head` on every start, so self-hosters upgrade in place.
