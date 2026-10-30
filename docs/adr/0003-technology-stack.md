# 0003 — Technology stack

- **Status:** Accepted
- **Date:** 2026-10-30

## Context

Four parts with different runtimes: a browser SDK, a web console, an API with event ingestion,
and (later) a Chrome extension. Self-hosters should deploy as little as possible.

## Options

1. TypeScript everywhere (Node API).
2. Next.js full-stack for Studio + API.
3. **Python API + TypeScript front ends.**

## Decision

- **Backend:** Python, FastAPI, SQLAlchemy 2, Alembic, Postgres 16.
- **Studio:** React, TypeScript, Vite.
- **SDK:** TypeScript with no runtime dependencies, rendered in a Shadow DOM root, under
  30 KB gzipped.
- **Builder extension:** TypeScript, Chrome Manifest V3 (phase 2).
- **Packaging:** one Docker image — the backend serves the built Studio and `/sdk.js` — plus
  Postgres. Compose for local and simple deployments.

## Consequences

- Two toolchains (Python and Node). Contracts between them live as JSON Schemas in
  `code/shared/schema/`; TypeScript types are generated from them so the two sides cannot drift.
- Shadow DOM isolates step styling from host-page CSS in both directions.
