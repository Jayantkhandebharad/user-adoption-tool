# 0005 — Email and password sign-in for Studio

- **Status:** Accepted
- **Date:** 2026-10-30

## Context

Studio needs authenticated team members with roles (admin, editor, publisher, viewer). Many
organisations want SSO, but it adds setup for small self-hosters.

## Decision

MVP uses email and password: Argon2id hashes, server-side sessions in an `HttpOnly`,
`Secure`, `SameSite=Lax` cookie. The first admin is created on first run; others are invited by
email (SMTP). OIDC sign-in (Google, Okta, Entra ID…) is phase 2.

## Consequences

- Needs SMTP for invites and password resets; Mailpit emulates it locally.
- Session storage lives in Postgres (no Redis), consistent with ADR 0004.
