# Architecture Decision Records

An ADR records one significant decision: the context, the options, what we chose and the
consequences. They are short and immutable — to change a decision, write a new ADR that
supersedes the old one and update the old one's status line.

Write one when a choice is hard to reverse or affects several parts of the code: a framework,
a datastore, a public API shape, a security model, a licence.

Copy [`template.md`](template.md) to `NNNN-short-title.md` with the next free number.

| # | Decision | Status |
|---|---|---|
| [0001](0001-record-architecture-decisions.md) | Record architecture decisions | Accepted |
| [0002](0002-self-hosted-single-tenant.md) | Open source, self-hosted, single-tenant | Accepted |
| [0003](0003-technology-stack.md) | Technology stack | Accepted |
| [0004](0004-postgres-for-events.md) | Postgres as the only datastore, including events | Accepted |
| [0005](0005-studio-authentication.md) | Email and password sign-in for Studio | Accepted |
| [0006](0006-apache-2-licence.md) | Apache-2.0 licence | Accepted |
| [0007](0007-repository-layout.md) | Repository layout | Accepted |
