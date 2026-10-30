# backend

FastAPI service. One process exposes:

- **Management API** (`/api/…`) — used by Studio; session auth with roles.
- **SDK API** (`/sdk/v1/…`) — used by the browser SDK; allowed-origin check and optional
  identity verification.
- **Static files** — the built Studio at `/` and the SDK bundle at `/sdk.js`.

Planned layout: `app/` (routers, services, models), `migrations/` (Alembic), `tests/`.
Setup and commands are added here in milestone M0.
