# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Ground rules

- **Never write the name of the commercial product this project is modelled on** — not in code,
  comments, docs, tests, fixtures, config, branch names, commit messages or PR text, and not its
  domains or SDK identifiers either. Describe features generically ("product-adoption tool",
  "in-app guidance"). The name is recorded in Claude's project memory; grep the diff and the
  commit message for it (case-insensitive) before every commit.
- **Commit as `jntkhandebharad@gmail.com`** (Jayant Khandebharad). The repo's local git config
  already sets this; never override it with `--author` or the global identity.
- Working product name is the placeholder **`guide`**: SDK global `window.Guide`, page anchors
  `data-guide="…"`. Expect a rename later, so keep the name in as few places as possible.

## Status

The project is in the planning phase: there is no code, build tooling or tests yet. The plan,
decisions and milestones (M0–M5) are in `docs/PLAN.md` — read it before starting work. Add the
real build / lint / test / single-test commands here once M0 (foundations) lands.

## Architecture (planned)

An open-source, **self-hosted, single-tenant** product-adoption tool: guidance (Flows of modal /
slideout / tooltip / hotspot / redirect steps) shown inside the self-hoster's own web app and
changed without a deploy of that app. One instance = one organisation; there are no accounts or
`account_id`s — don't add tenant scoping.

| Path | Part | Stack |
|---|---|---|
| `packages/sdk/` | Browser SDK loaded by a snippet on the customer's page | TypeScript, no runtime deps, Shadow DOM |
| `packages/schema/` | JSON Schemas for experience content; source of TS types | JSON Schema |
| `apps/studio/` | Web console: authoring, targeting, publish, analytics, settings | React + TS + Vite |
| `apps/demo/` | Plain page that loads the SDK, used for manual testing | HTML |
| `services/api/` | Management API (Studio) + SDK API + event ingestion; also serves built Studio and `/sdk.js` | FastAPI, SQLAlchemy 2, Alembic, Postgres |
| `apps/builder-extension/` | Chrome extension element picker (phase 2) | TS, MV3 |

Cross-cutting rules that span these parts:

- **Targeting is split.** Per page view the SDK posts user activity; the API evaluates audience,
  frequency, schedule and the account-wide cap server-side and returns qualifying experiences.
  The SDK then checks what only the browser can (URL match, target element present) and shows
  **at most one Flow per page view**, chosen by priority then weight. Manual triggers
  (`Guide.show(id)`) bypass all targeting. Evaluation order is in `docs/PLAN.md` §6.
- **Published content is immutable.** Publishing snapshots the draft into `experience_versions`;
  the SDK only receives published versions, or a draft when a signed preview token is present.
- **One content schema.** Flow/step shape is defined once in `packages/schema` and used for API
  validation and for SDK/Studio types — change it there, not in each consumer.
- **Deployment is one unit.** Self-hosters run the `api` container plus Postgres and configure it
  with env vars; the host app installs the SDK with `Guide.init({ apiUrl })` pointing at their
  instance. Keep it that way — no extra required services without a strong reason.
- **SDK API security** = allowed-origins list (CORS + server check) plus optional identity
  verification (`userHash` = HMAC-SHA256 of the user id with a secret from Studio settings).
  The allowed-origins list is also how dev / qa / prod or several apps share one instance.
  See `docs/PLAN.md` §3.1.
- **Rich text** is sanitised on save (API) and again before render (SDK).
