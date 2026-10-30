# Plan

Working name: **guide** (SDK global `window.Guide`, anchors `data-guide="…"`). Renamed later.

An open-source, self-hosted product-adoption tool: in-app guidance (tours, tips, checklists,
surveys) shown inside your own web app and changed without a deploy of that app. Each team runs
its own instance; one instance serves one organisation.

## 1. Decisions

| Topic | Decision |
|---|---|
| MVP | SDK + Studio + Flows, with targeting, publish and basic analytics |
| Backend | Python: FastAPI, SQLAlchemy 2 + Alembic, Postgres 16 |
| Studio | React + TypeScript + Vite |
| SDK | TypeScript, no runtime deps, rendered in Shadow DOM, target < 30 KB gzipped |
| Builder | Chrome extension (MV3, TypeScript) — phase 2 |
| Licence | Apache-2.0 (`LICENSE`) |
| Distribution | Open source, self-hosted. Docker images + one `docker-compose.yml`; no hosted service from us |
| Tenancy | **Single-tenant.** One instance = one organisation. No accounts, no `account_id` columns, no per-tenant isolation |
| SDK config | The host app gives the SDK the **URL of its backend**; no account id (see §3.1) |
| Environments | One instance can serve many host URLs (dev / qa / prod / several apps) via an allowed-origins list; page targeting can filter by host |

## 2. Parts

| Part | MVP | Phase 2+ |
|---|---|---|
| **SDK** (`packages/sdk`) | served by the backend at `/sdk.js` and published to npm; `init({ apiUrl })`, `identify`, `group`, `track`, `page`, `show`, `reset`, `debug`, `on/off`; SPA URL detection; Flow renderer | Pins, Checklists, Banners, NPS, Launchpad, Embeds renderers; localization |
| **Studio** (`apps/studio`) | first-run admin setup, sign-in, experiences list, form-based Flow editor (paste a CSS selector), targeting, draft → publish → archive, preview link, users & events browser, experience analytics, settings (allowed origins, install snippet, team, identity-verification secret) | segments UI, themes editor, A/B, dashboards, key moments, campaigns |
| **API** (`services/api`) | management API for Studio; SDK API (activity in, qualifying experiences out); event ingestion | public API, webhooks, integrations, workflows (email) |
| **Builder** (`apps/builder-extension`) | — | element picker, step authoring over the live page, test mode |

## 3. Architecture

```
                         ┌──────────── your instance (one docker-compose) ────────────┐
host app ──<script>──► SDK ──HTTPS──► SDK API ─┐                                      │
                         │                     ├─► Postgres                           │
Studio (React) ──────────┼──► Management API ──┘                                      │
Builder ext. (phase 2) ──┘                                                            │
                         └────────────────────────────────────────────────────────────┘
```

Studio and both APIs ship as one deployable: the API container also serves the built Studio
and `/sdk.js`, so a self-hoster runs `api` + `postgres` and sets a handful of env vars
(`DATABASE_URL`, `PUBLIC_URL`, `SECRET_KEY`, `ALLOWED_ORIGINS`).

### 3.1 Installing the SDK in a host app

```html
<script src="https://guide.example.com/sdk.js"></script>
<script>
  Guide.init({ apiUrl: "https://guide.example.com" });
  Guide.identify(user.id, { role: user.role }, { userHash: "<HMAC from your server>" });
</script>
```

No account id: a single-tenant instance has nothing to select. Security comes from two things
an account id would not give anyway (it is visible in page source):

1. **Allowed origins** — the SDK API answers only browser requests whose `Origin` is on the
   instance's list (CORS + server check). Stops other sites from embedding your guidance.
2. **Identity verification** (optional, recommended for production) — the host app's server
   signs the user id with a secret from Studio settings (`HMAC-SHA256(secret, userId)`) and
   passes it as `userHash`. When enforced, the API rejects unsigned or wrong ids, so nobody can
   read or pollute another user's state by calling `identify` with their id.

If a self-hoster later runs several separate products on one instance, an optional
**environment key** can be added then; it is not in the MVP.

- **SDK flow per page view:** SDK sends `activity` (user id, properties, page URL, queued
  events). The API stores it, evaluates targeting server-side (audience, frequency, schedule,
  account cap) and returns the qualifying experiences for this user. The SDK then checks the
  page-level conditions it can only check in the browser (URL match, target element present),
  picks at most **one Flow** by priority/weight, and renders it.
- **Published content is immutable:** publishing snapshots the draft into an
  `experience_versions` row. The SDK only ever receives published versions (or a draft when a
  signed preview token is present).
- **Rendering:** Shadow DOM root so host-page CSS cannot break steps and our CSS cannot leak.
- **Hosts:** the instance lists allowed origins; the SDK API rejects other origins and page
  targeting can filter by host, so dev / qa / prod (or several apps) share one instance.

## 4. Data model (first cut)

| Table | Key columns |
|---|---|
| `settings` | single row: instance name, frequency cap, identity-verification secret + enforce flag |
| `allowed_origins` | origin, label (e.g. "prod", "staging") |
| `team_members` | email, password_hash, role (admin/editor/publisher/viewer) |
| `end_users` | external_id (unique), properties jsonb, first_seen, last_seen, session_count |
| `groups` | external_id (unique), properties jsonb |
| `events` | end_user_id, name, properties jsonb, url, session_id, ts (partition by month) |
| `experiences` | type, name, status, draft jsonb, targeting jsonb, priority, weight, schedule |
| `experience_versions` | experience_id, version, content jsonb, targeting jsonb, published_at, published_by |
| `experience_states` | end_user_id, experience_id, times_shown, last_shown, completed_at, dismissed_at |

Built-in events written by the SDK: `page_view`, `flow_started`, `flow_step_seen`,
`flow_completed`, `flow_skipped`, `flow_button_clicked`.

## 5. Flow content schema (MVP)

A Flow is an ordered list of steps. Step types: `modal`, `slideout`, `tooltip`, `hotspot`,
`redirect`. Each step has: target selector (tooltip/hotspot), placement, rich-text body
(sanitised HTML), buttons with an action (`next`, `prev`, `end`, `url`, `show_experience`,
`track_event`), skippable flag, optional page-URL condition (multi-page flows). Schema lives
in one JSON Schema file shared by API (validation) and SDK/Studio (generated TS types).

## 6. Targeting (MVP)

Evaluated in this order:

1. **Trigger:** automatic, manual (`Guide.show(id)` / link — bypasses everything below), on event.
2. **Pages:** URL equals / contains / regex, host (allowed origin).
3. **Audience:** user property, group property, event seen / not seen (with count and window),
   experience seen / completed.
4. **Frequency:** once ever, once per session, every N days, every time; "show again if not completed".
5. **Schedule:** start / end date.
6. **Account-wide cap:** at most N experiences per user per period.
7. **Tie-break:** priority, then weight.

## 7. Milestones

| # | Milestone | Done when |
|---|---|---|
| M0 | **Foundations** — repo layout, docker-compose (api serving Studio, postgres), env-var config, first-run admin setup, Studio sign-in, lint/format/test in CI, pre-commit check that blocks the reference product's name | `docker compose up` → create admin → empty Studio; CI green |
| M1 | **SDK core + ingestion** — `/sdk.js`, `init({ apiUrl })`, `identify/group/track/page/reset`, URL detection, allowed-origins check, identity verification, activity endpoint, users & events browser in Studio, `debug()` panel | a demo page's user and events appear in Studio; a request from an unlisted origin or with a bad `userHash` is rejected |
| M2 | **Flow renderer** — schema, modal/slideout/tooltip/hotspot/redirect in Shadow DOM, buttons, multi-page flows, default theme | a hand-written Flow JSON renders on the demo page |
| M3 | **Studio authoring** — experiences list, Flow editor, draft/publish/archive, versions, preview link | a Flow built in Studio shows on the demo page after Publish |
| M4 | **Targeting engine** — section 6, one Flow per page view, `experience_states` | targeting test matrix passes |
| M5 | **Analytics** — views, completions, step drop-off, dismissals, goal (event after seen) | per-Flow funnel chart in Studio |

Phase 2 (order to be agreed): Builder extension → Pins → Checklists → Banners → NPS →
Segments & themes → Launchpad → A/B → public API & webhooks → localization → Embeds →
Workflows (email). Self-hosting extras alongside: Helm chart, backup/restore docs, upgrade
notes per release.

## 8. Repo layout

```
apps/studio/              React console
apps/demo/                plain test page that loads the SDK
packages/sdk/             browser SDK
packages/schema/          JSON Schemas + generated TS types
services/api/             FastAPI app, Alembic migrations, tests
docker-compose.yml
docs/
```

## 9. Privacy and security

- The SDK stores whatever the host sends; document that hosts should not send sensitive data.
- Rich text is sanitised server-side on save and client-side before render.
- Custom HTML/JS steps are phase 2 and admin-only.
- SDK API: allowed-origin check + optional identity verification (§3.1) + rate limits;
  management API: session auth with roles.
- All data stays on the self-hoster's infrastructure; the tool makes no outbound calls
  (no telemetry) unless an integration is configured.

## 10. Open questions

1. Studio auth: email + password to start, with optional OIDC (Google, Okta, Entra) later?
2. Event volume to design for (Postgres partitions are fine to ~100M rows; beyond that a
   column store)?
3. Mobile SDKs: confirm out of scope.
