"""Instance configuration, read from environment variables (or a local `.env` file).

Defaults suit local development against the emulators in infra/docker/compose.dev.yaml.
"""

from functools import cached_property
from pathlib import Path
from urllib.parse import urlsplit

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "postgresql+psycopg://guide:guide@localhost:55432/guide"
    # Where people open Studio. Used for the session cookie's Secure flag and the CSRF origin
    # check. In development that is the Vite dev server, which proxies /api to this process.
    public_url: str = "http://localhost:5173"
    # If set, creating the first admin requires this token, so nobody else can claim a freshly
    # deployed instance before its operator does.
    setup_token: str | None = None
    session_ttl_hours: int = Field(default=24 * 7, gt=0)
    # Built Studio files to serve at "/". Unset in development (Vite serves Studio).
    studio_dist: Path | None = None

    @field_validator("setup_token", "studio_dist", mode="before")
    @classmethod
    def _empty_is_unset(cls, value: object) -> object:
        # Compose passes `SETUP_TOKEN: ${SETUP_TOKEN:-}` as an empty string when unset.
        return None if value == "" else value

    @cached_property
    def public_origin(self) -> str:
        parts = urlsplit(self.public_url)
        return f"{parts.scheme}://{parts.netloc}"

    @property
    def secure_cookies(self) -> bool:
        return self.public_url.startswith("https://")
