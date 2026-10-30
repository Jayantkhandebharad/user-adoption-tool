# docker

| File | Purpose | Status |
|---|---|---|
| `compose.dev.yaml` | Local emulators for every external resource the app uses | available |
| `Dockerfile` | One multi-stage image: builds Studio and the SDK, then the backend that serves them. Build context is the repository root | M0 |
| `compose.yaml` | Self-host stack: the app image + Postgres | M0 |
| `dev/` | Config and seed files mounted into the emulators | |

## Local emulators

| Service | Emulates | Address |
|---|---|---|
| `postgres` | the database | `localhost:55432`, user / password / db `guide` |
| `mailpit` | an SMTP server (team invites, password resets); web UI shows caught mail | SMTP `localhost:1025`, UI http://localhost:8025 |

Start and stop them with [`scripts/dev-services.sh`](../../scripts/dev-services.sh):

```bash
scripts/dev-services.sh up
scripts/dev-services.sh down
```

When the app starts using a new external resource (for example object storage for uploaded
images), add its emulator here in the same change.

Host ports can be changed with `GUIDE_POSTGRES_PORT`, `GUIDE_SMTP_PORT` and
`GUIDE_MAILPIT_UI_PORT` if they clash with something already running.
