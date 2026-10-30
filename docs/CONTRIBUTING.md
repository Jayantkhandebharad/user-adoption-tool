# Contributing

Thanks for helping. This project is an open-source, self-hosted tool for in-app guidance:
tours, tips, checklists and surveys inside your own web app. By taking part you agree to the
[Code of Conduct](CODE_OF_CONDUCT.md).

## Ways to help

- **Report bugs and request features** — see [`issues/`](issues/README.md).
- **Fix an issue** — look for `good first issue` and `help wanted` labels.
- **Improve docs** — anything under `docs/` or a part's README.
- **Review pull requests** and try out pre-releases on your own instance.

## Before you write code

- **Small fixes** (typos, clear bugs, docs): open a PR directly.
- **Anything larger** (a feature, a new dependency, a change to an API, schema or the SDK's
  public surface): open or find an issue first and wait for it to be marked `accepted`, so
  your work isn't wasted.
- **New behaviour or contract:** add a spec in [`specs/`](specs/README.md) in the same PR, or
  before it.
- **A hard-to-reverse choice** (framework, datastore, security model): propose an ADR in
  [`adr/`](adr/README.md).

## Repository map

| Path | What |
|---|---|
| `code/backend/` | FastAPI API (Python) |
| `code/studio/` | Web console (React + TypeScript) |
| `code/sdk/` | Browser SDK (TypeScript) |
| `code/shared/` | JSON Schemas shared by all parts |
| `infra/docker/` | Docker image, Compose files, local emulators |
| `scripts/` | Helper scripts |
| `docs/` | Plans, specs, ADRs, these guides |

The current roadmap is [`plans/mvp.md`](plans/mvp.md).

## Local development

You need Docker. Local emulators for everything the app talks to (Postgres, an SMTP catcher)
run from one Compose file:

```bash
scripts/dev-services.sh up
```

Toolchain setup and the commands to build, lint and test each part are in that part's README
(`code/<part>/README.md`). They are being added during milestone M0.

## Making a change

1. Fork the repo and create a branch from `main`: `fix/short-description`,
   `feat/short-description` or `docs/short-description`.
2. Keep each PR to one logical change. Unrelated clean-ups go in their own PR.
3. Add or update tests with the change. Bug fixes come with a test that fails without the fix.
4. Update docs that the change makes wrong: the part's README, a spec, the plan.
5. If you change a schema in `code/shared/schema/`, regenerate the types and update both the
   backend and the TypeScript consumers in the same PR.
6. Database changes come with an Alembic migration that runs forward on an existing instance.
   Self-hosters upgrade in place, so never edit a migration that has been released.
7. Write commit messages in the imperative mood ("Add hotspot step", not "Added…"), with a
   short first line and a body explaining *why* when it isn't obvious.

## Pull requests

- Fill in the PR template, and link the issue (`Closes #123`).
- CI must pass: lint, type checks, tests, build.
- UI changes need a screenshot or short recording.
- A maintainer reviews within about a week. Address comments with new commits; we squash on
  merge.

## Licence

The project is licensed under [Apache-2.0](../LICENSE). By submitting a contribution you agree
it is licensed under the same terms (Apache-2.0, section 5). No separate CLA is required.
