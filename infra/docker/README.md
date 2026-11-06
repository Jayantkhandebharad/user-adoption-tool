# docker

| File | Purpose |
|---|---|
| `Dockerfile` | One multi-stage image: builds Studio, then the backend that serves it. Build context is the repository root |
| `Dockerfile.dockerignore` | Ignore rules for that build (kept here instead of the repo root) |
| `entrypoint.sh` | Runs `alembic upgrade head`, then the server |
| `compose.yaml` | Self-host stack: the app image + Postgres |
| `compose.dev.yaml` | Local emulators for development |
| `dev/` | Config and seed files mounted into the emulators |

## Self-hosting

```bash
docker compose -f infra/docker/compose.yaml up -d --build
```

Open http://localhost:8000 and create the first admin account. Schema migrations run
automatically on every start, so upgrading is `git pull` and the same command.

Configure with environment variables (or an `.env` file next to where you run compose):

| Variable | Default | Meaning |
|---|---|---|
| `PUBLIC_URL` | `http://localhost:8000` | URL people use to open Studio. Must match exactly (scheme, host, port): it drives the cross-origin check and, when `https://`, the `Secure` cookie flag |
| `SETUP_TOKEN` | unset | If set, creating the first admin requires this value. Set it whenever the instance is reachable by others before you finish setup |
| `POSTGRES_PASSWORD` | `guide` | Database password. The database port is not published, but change it anyway |
| `GUIDE_PORT` | `8000` | Host port for the app |
| `WEB_CONCURRENCY` | `2` | Server worker processes |
| `FORWARDED_ALLOW_IPS` | `127.0.0.1` | Proxies whose `X-Forwarded-*` headers are trusted. Set to your reverse proxy's address when TLS terminates there |

The app reads `DATABASE_URL` directly; compose builds it from `POSTGRES_PASSWORD`. To use a
managed Postgres instead, run the image on its own with `DATABASE_URL` set
(`postgresql+psycopg://user:password@host:5432/db`).

Put the app behind a TLS-terminating reverse proxy (Caddy, nginx, a cloud load balancer) for
anything beyond local use, and set `PUBLIC_URL` to the `https://` address.

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

Host ports can be changed with `GUIDE_POSTGRES_PORT`, `GUIDE_SMTP_PORT` and
`GUIDE_MAILPIT_UI_PORT` if they clash with something already running.

When the app starts using a new external resource (for example object storage for uploaded
images), add its emulator here in the same change.
