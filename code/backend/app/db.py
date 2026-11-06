from collections.abc import Iterator

from fastapi import Request
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker


class Base(DeclarativeBase):
    pass


def make_sessionmaker(database_url: str) -> sessionmaker[Session]:
    engine = create_engine(database_url, pool_pre_ping=True)
    return sessionmaker(engine, expire_on_commit=False)


def get_db(request: Request) -> Iterator[Session]:
    """One database session per request; commits on success, rolls back on error."""
    factory: sessionmaker[Session] = request.app.state.sessionmaker
    with factory() as db:
        try:
            yield db
            db.commit()
        except Exception:
            db.rollback()
            raise
