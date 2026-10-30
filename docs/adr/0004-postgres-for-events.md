# 0004 — Postgres as the only datastore, including events

- **Status:** Accepted
- **Date:** 2026-10-30

## Context

Every page view, flow step and custom event is stored. Column stores (ClickHouse etc.) handle
large volumes better, but each extra service is something every self-hoster must run.

## Options

1. **Postgres only**, `events` partitioned by month.
2. Pluggable event store with ClickHouse as an option from day one.

## Decision

Postgres only. Design for about 100M events per instance (roughly 10k monthly active users for
a couple of years).

## Consequences

- One datastore to deploy, back up and upgrade.
- Analytics queries must use indexes and monthly partitions; old partitions can be dropped or
  archived.
- If real users outgrow it, a column store can be introduced behind the analytics queries by a
  later ADR.
