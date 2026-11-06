# One image: builds Studio, then the backend that serves it (and, from M1, the SDK).
# Build from the repository root:
#   docker build -f infra/docker/Dockerfile -t guide .

FROM node:22-alpine AS studio
WORKDIR /src/code
COPY code/package.json code/package-lock.json ./
COPY code/studio/package.json studio/
RUN npm ci --workspace studio --include-workspace-root=false
COPY code/studio studio
RUN npm run build --workspace studio

FROM python:3.13-slim AS app
COPY --from=ghcr.io/astral-sh/uv:0.11.2 /uv /usr/local/bin/uv
ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PYTHON_DOWNLOADS=never \
    UV_PROJECT_ENVIRONMENT=/app/.venv
WORKDIR /app
COPY code/backend/pyproject.toml code/backend/uv.lock code/backend/.python-version ./
RUN uv sync --frozen --no-dev --no-install-project
COPY code/backend/alembic.ini ./
COPY code/backend/app app
COPY code/backend/migrations migrations
COPY --from=studio /src/code/studio/dist /app/studio
COPY infra/docker/entrypoint.sh /entrypoint.sh

RUN useradd --system --uid 10001 --no-create-home guide
USER guide
ENV PATH=/app/.venv/bin:$PATH \
    STUDIO_DIST=/app/studio \
    PUBLIC_URL=http://localhost:8000
EXPOSE 8000
HEALTHCHECK --interval=10s --timeout=3s --start-period=20s \
  CMD ["python", "-c", "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/api/health')"]
ENTRYPOINT ["/entrypoint.sh"]
