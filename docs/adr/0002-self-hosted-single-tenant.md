# 0002 — Open source, self-hosted, single-tenant

- **Status:** Accepted
- **Date:** 2026-10-30

## Context

Commercial product-adoption tools are hosted, multi-tenant services. This project is open
source: each team runs its own instance on its own infrastructure and keeps its data there.

## Options

1. **Multi-tenant** (accounts, `account_id` on every row, per-tenant isolation) — lets one
   instance serve many organisations, but adds scoping to every query, tenant-aware auth and
   billing-shaped concepts nobody self-hosting needs.
2. **Single-tenant** — one instance serves one organisation.

## Decision

Single-tenant. No accounts or account id. The host app configures the SDK with the URL of its
instance (`Guide.init({ apiUrl })`). One instance can serve several host URLs (dev / qa / prod,
or several apps) through an allowed-origins list, and page targeting can filter by host.

SDK API security comes from the allowed-origins check plus optional identity verification
(`userHash` = HMAC-SHA256 of the user id with a secret from Studio settings). An account id
would add nothing: it is visible in page source.

## Consequences

- Simpler schema, queries and auth.
- Teams wanting full separation between products run separate instances. An optional
  environment key can be added later if one instance must host unrelated products.
- No telemetry or outbound calls unless an integration is configured.
