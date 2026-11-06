"""First-run setup, sign-in and sessions for Studio (management API)."""

import secrets
from datetime import UTC, datetime, timedelta
from typing import Annotated

from fastapi import APIRouter, Cookie, Depends, HTTPException, Request, Response, status
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy import delete, func, select, text
from sqlalchemy.orm import Session

from app.config import Settings
from app.db import get_db
from app.models import Role, StudioSession, TeamMember
from app.security import hash_password, hash_token, new_session_token, verify_password

SESSION_COOKIE = "guide_session"
MIN_PASSWORD_LENGTH = 12
# Arbitrary constant for pg_advisory_xact_lock: serialises concurrent first-run setups.
_SETUP_LOCK_ID = 7_301_001

router = APIRouter(prefix="/api", tags=["auth"])
DB = Annotated[Session, Depends(get_db)]


def get_settings(request: Request) -> Settings:
    settings: Settings = request.app.state.settings
    return settings


SettingsDep = Annotated[Settings, Depends(get_settings)]


class MemberOut(BaseModel):
    id: str
    email: str
    name: str
    role: Role

    @classmethod
    def of(cls, member: TeamMember) -> "MemberOut":
        return cls(id=str(member.id), email=member.email, name=member.name, role=member.role)


class SetupStatus(BaseModel):
    needs_setup: bool
    token_required: bool


class SetupIn(BaseModel):
    email: EmailStr
    name: str = Field(min_length=1, max_length=200)
    password: str = Field(min_length=MIN_PASSWORD_LENGTH, max_length=1024)
    setup_token: str | None = None


class LoginIn(BaseModel):
    email: EmailStr
    password: str = Field(max_length=1024)


def _start_session(db: Session, response: Response, settings: Settings, member: TeamMember) -> None:
    token, token_hash = new_session_token()
    now = datetime.now(UTC)
    ttl = timedelta(hours=settings.session_ttl_hours)
    db.execute(delete(StudioSession).where(StudioSession.expires_at <= now))  # housekeeping
    db.add(StudioSession(token_hash=token_hash, member_id=member.id, expires_at=now + ttl))
    member.last_login_at = now
    response.set_cookie(
        SESSION_COOKIE,
        token,
        max_age=int(ttl.total_seconds()),
        httponly=True,
        secure=settings.secure_cookies,
        samesite="lax",
        path="/",
    )


def current_member(
    db: DB, settings: SettingsDep, token: Annotated[str | None, Cookie(alias=SESSION_COOKIE)] = None
) -> TeamMember:
    """Dependency: the signed-in team member, or 401. Extends sessions past half their life."""
    if not token:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Not signed in")
    now = datetime.now(UTC)
    session = db.get(StudioSession, hash_token(token))
    if session is None or session.expires_at <= now:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Not signed in")
    ttl = timedelta(hours=settings.session_ttl_hours)
    if session.expires_at - now < ttl / 2:
        session.expires_at = now + ttl
    member = db.get(TeamMember, session.member_id)
    if member is None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Not signed in")
    return member


CurrentMember = Annotated[TeamMember, Depends(current_member)]


def _needs_setup(db: Session) -> bool:
    return db.scalar(select(func.count()).select_from(TeamMember)) == 0


@router.get("/setup/status")
def setup_status(db: DB, settings: SettingsDep) -> SetupStatus:
    return SetupStatus(
        needs_setup=_needs_setup(db), token_required=settings.setup_token is not None
    )


@router.post("/setup", status_code=status.HTTP_201_CREATED)
def setup(body: SetupIn, response: Response, db: DB, settings: SettingsDep) -> MemberOut:
    """Create the first admin. Only works while the instance has no team members."""
    if settings.setup_token is not None and not secrets.compare_digest(
        (body.setup_token or "").encode(), settings.setup_token.encode()
    ):
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Invalid setup token")
    db.execute(text("SELECT pg_advisory_xact_lock(:id)"), {"id": _SETUP_LOCK_ID})
    if not _needs_setup(db):
        raise HTTPException(status.HTTP_409_CONFLICT, "This instance is already set up")
    member = TeamMember(
        email=body.email.lower(),
        name=body.name.strip(),
        password_hash=hash_password(body.password),
        role=Role.admin,
    )
    db.add(member)
    db.flush()
    _start_session(db, response, settings, member)
    return MemberOut.of(member)


@router.post("/auth/login")
def login(body: LoginIn, response: Response, db: DB, settings: SettingsDep) -> MemberOut:
    member = db.scalar(select(TeamMember).where(TeamMember.email == body.email.lower()))
    if not verify_password(member.password_hash if member else None, body.password):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Wrong email or password")
    assert member is not None
    _start_session(db, response, settings, member)
    return MemberOut.of(member)


@router.post("/auth/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(
    response: Response,
    db: DB,
    token: Annotated[str | None, Cookie(alias=SESSION_COOKIE)] = None,
) -> None:
    if token:
        db.execute(delete(StudioSession).where(StudioSession.token_hash == hash_token(token)))
    response.delete_cookie(SESSION_COOKIE, path="/")


@router.get("/auth/me")
def me(member: CurrentMember) -> MemberOut:
    return MemberOut.of(member)
