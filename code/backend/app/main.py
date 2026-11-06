from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from sqlalchemy import text
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.responses import Response
from starlette.types import ASGIApp

from app import auth
from app.config import Settings
from app.db import make_sessionmaker
from app.static import StudioFiles

UNSAFE_METHODS = {"POST", "PUT", "PATCH", "DELETE"}


class StudioOriginCheck(BaseHTTPMiddleware):
    """CSRF defence for the management API, on top of SameSite=Lax cookies: browsers send
    Origin on unsafe requests, and it must be the Studio origin. Requests without Origin
    (curl, server-to-server) carry no ambient browser cookies and pass."""

    def __init__(self, app: ASGIApp, allowed_origin: str) -> None:
        super().__init__(app)
        self.allowed_origin = allowed_origin

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        origin = request.headers.get("origin")
        if (
            request.method in UNSAFE_METHODS
            and request.url.path.startswith("/api/")
            and origin is not None
            and origin != self.allowed_origin
        ):
            return JSONResponse({"detail": "Cross-origin request refused"}, status_code=403)
        return await call_next(request)


def create_app(settings: Settings | None = None) -> FastAPI:
    settings = settings or Settings()
    app = FastAPI(title="guide", docs_url="/api/docs", openapi_url="/api/openapi.json")
    app.state.settings = settings
    app.state.sessionmaker = make_sessionmaker(settings.database_url)
    app.add_middleware(StudioOriginCheck, allowed_origin=settings.public_origin)
    app.include_router(auth.router)

    @app.get("/api/health", tags=["meta"])
    def health() -> JSONResponse:
        try:
            with app.state.sessionmaker() as db:
                db.execute(text("SELECT 1"))
        except Exception:
            return JSONResponse({"status": "error", "database": "unreachable"}, status_code=503)
        return JSONResponse({"status": "ok"})

    if settings.studio_dist is not None:
        app.mount("/", StudioFiles(settings.studio_dist), name="studio")
    return app
