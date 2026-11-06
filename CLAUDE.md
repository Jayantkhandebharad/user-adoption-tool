# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Ground rules

- **Never write the name of the commercial product this project is modelled on** — not in code,
  comments, docs, tests, fixtures, config, branch names, commit messages or PR text, and not its
  domains or SDK identifiers either. Describe features generically ("product-adoption tool",
  "in-app guidance"). The name is recorded in Claude's project memory; grep the diff and the
  commit message for it (case-insensitive) before every commit. `scripts/check-blocked-terms.py`
  enforces this from git hooks (`scripts/install-git-hooks.sh`) and CI; it stores only a hash.
- **Commit as `jntkhandebharad@gmail.com`** (Jayant Khandebharad). The repo's local git config
  already sets this; never override it with `--author` or the global identity.
- Working product name is the placeholder **`guide`**: SDK global `window.Guide`, page anchors
  `data-guide="…"`. Expect a rename later, so keep the name in as few places as possible.

## Status

M0 (foundations) is built: backend with first-run setup, sign-in and sessions; Studio with
setup / sign-in / empty home; Docker image and self-host compose; CI. Read `docs/plans/mvp.md`
(scope, milestones M0–M5) and `docs/adr/` (decisions and why) before starting work.

## Commands

```bash
scripts/dev-services.sh up      # emulators: Postgres localhost:55432 (guide/guide/guide),
                                # Mailpit SMTP :1025, UI :8025. Also: down | reset | ps | logs
```

Backend (`code/backend`, uv):

```bash
uv sync && uv run alembic upgrade head
uv run uvicorn app.main:create_app --factory --reload --port 8000
uv run ruff format . && uv run ruff check . && uv run mypy      # mypy is strict
uv run pytest                                                   # needs the Postgres emulator
uv run pytest tests/test_auth.py::test_login_and_logout         # single test
uv run alembic revision -m "..."                                # new migration (hand-edit it)
```

Studio (run from `code/`, the npm workspace root):

```bash
npm install
npm run dev --workspace studio          # :5173, proxies /api to :8000
npm run check                           # Biome lint+format; `npm run format` to fix
npm run typecheck --workspace studio && npm test --workspace studio
cd studio && npx vitest run src/App.test.tsx -t "signs out"     # single test
```

Whole stack as a self-hoster runs it: `docker compose -f infra/docker/compose.yaml up -d --build`
(app on :8000; `GUIDE_PORT` / `PUBLIC_URL` to change). Settings are listed in
`infra/docker/README.md`.

When the app starts using a new external resource, add its emulator to
`infra/docker/compose.dev.yaml` in the same change.

## Repository layout

Keep the root clean: only `README.md`, `LICENSE`, `CLAUDE.md` and dotfiles tools require there
(ADR 0007). Source lives in `code/<part>/`, Docker/Compose files in `infra/docker/`, cloud
reference deployments in `infra/aws|azure/`, helpers in `scripts/`. The npm workspace is rooted
in `code/`. Docs: `docs/plans/` (what and when), `docs/specs/` (how, one per feature or
contract), `docs/adr/` (why; immutable, supersede with a new ADR), `docs/issues/` (issue
process). A change that reverses a recorded decision needs a new ADR; a new contract or
behaviour needs a spec.

## Architecture

An open-source, **self-hosted, single-tenant** product-adoption tool: guidance (Flows of modal /
slideout / tooltip / hotspot / redirect steps) shown inside the self-hoster's own web app and
changed without a deploy of that app. One instance = one organisation; there are no accounts or
`account_id`s — don't add tenant scoping.

Built so far (M0):

- **Backend** — `create_app(settings)` in `app/main.py` builds everything from a `Settings`
  object (env vars, defaults suit local dev); the engine lives on `app.state`, so tests build
  apps with overridden settings via the `make_client` fixture. Request DB sessions come from
  `get_db` (commit on success). Tests use a real Postgres `guide_test` database, migrated once
  per run with Alembic.
- **Studio auth** — server-side sessions: the `guide_session` cookie (HttpOnly, SameSite=Lax,
  Secure when `PUBLIC_URL` is https) holds a random token; only its SHA-256 is stored. CSRF
  defence: unsafe `/api/` requests whose `Origin` isn't `PUBLIC_URL`'s origin get 403, so in dev
  `PUBLIC_URL` is the Vite origin (:5173). First admin via `/api/setup`, serialised with a
  Postgres advisory lock, optionally gated by `SETUP_TOKEN`.
- **One image** — `infra/docker/Dockerfile` builds Studio, copies it into the backend image and
  sets `STUDIO_DIST`; the backend serves it with SPA fallback (unknown non-`/api` paths →
  `index.html`). The entrypoint runs migrations on every start.

Parts (full planned scope):

| Path | Part | Stack |
|---|---|---|
| `code/sdk/` | Browser SDK loaded by a snippet on the customer's page | TypeScript, no runtime deps, Shadow DOM |
| `code/shared/schema/` | JSON Schemas for experience content; source of TS types | JSON Schema |
| `code/studio/` | Web console: authoring, targeting, publish, analytics, settings | React + TS + Vite |
| `code/demo/` | Plain page that loads the SDK, used for manual testing | HTML |
| `code/backend/` | Management API (Studio) + SDK API + event ingestion; also serves built Studio and `/sdk.js` | FastAPI, SQLAlchemy 2, Alembic, Postgres |
| `code/builder-extension/` | Chrome extension element picker (phase 2) | TS, MV3 |

Cross-cutting rules that span these parts:

- **Targeting is split.** Per page view the SDK posts user activity; the API evaluates audience,
  frequency, schedule and the account-wide cap server-side and returns qualifying experiences.
  The SDK then checks what only the browser can (URL match, target element present) and shows
  **at most one Flow per page view**, chosen by priority then weight. Manual triggers
  (`Guide.show(id)`) bypass all targeting. Evaluation order is in `docs/plans/mvp.md` §6.
- **Published content is immutable.** Publishing snapshots the draft into `experience_versions`;
  the SDK only receives published versions, or a draft when a signed preview token is present.
- **One content schema.** Flow/step shape is defined once in `code/shared/schema` and used for API
  validation and for SDK/Studio types — change it there, not in each consumer.
- **Deployment is one unit.** Self-hosters run the `api` container plus Postgres and configure it
  with env vars; the host app installs the SDK with `Guide.init({ apiUrl })` pointing at their
  instance. Keep it that way — no extra required services without a strong reason.
- **SDK API security** = allowed-origins list (CORS + server check) plus optional identity
  verification (`userHash` = HMAC-SHA256 of the user id with a secret from Studio settings).
  The allowed-origins list is also how dev / qa / prod or several apps share one instance.
  See `docs/plans/mvp.md` §3.1 and ADR 0002.
- **Rich text** is sanitised on save (API) and again before render (SDK).
