# 0007 — Repository layout

- **Status:** Accepted
- **Date:** 2026-10-30

## Context

The repo holds several codebases (Python and TypeScript), infrastructure, and docs. A crowded
root makes it hard to find things.

## Decision

```
.github/   issue forms, PR template, CI workflows
code/      backend/, studio/, sdk/, shared/, builder-extension/, demo/
infra/     docker/ (image, compose files, local emulators), aws/, azure/
scripts/   developer and CI helper scripts
docs/      plans/, specs/, adr/, issues/, CONTRIBUTING, CODE_OF_CONDUCT, SECURITY
```

The root keeps only `README.md`, `LICENSE`, `CLAUDE.md` and dotfiles that tools require
there. The pnpm workspace is rooted in `code/`, not the repo root. Dockerfiles and Compose files
live in `infra/docker/`. Every external resource the app uses has a local emulator in
`infra/docker/compose.dev.yaml`.

## Consequences

Docker builds use the repository root as context with `-f infra/docker/Dockerfile`. Commands
are run from the relevant `code/<part>/` folder or through `scripts/`.
