"""The database connection. SPARC Cloud sets DATABASE_URL when you attach a database (Database tab)."""
import os

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker


def database_url() -> str:
    """postgresql://... -> postgresql+psycopg://... (the psycopg 3 driver). Never print this value: it holds the
    password."""
    url = os.environ.get("DATABASE_URL", "")
    if not url:
        raise RuntimeError("DATABASE_URL is not set: attach a database to this app (Database tab), then redeploy.")
    for prefix in ("postgresql://", "postgres://"):
        if url.startswith(prefix):
            return "postgresql+psycopg://" + url[len(prefix):]
    return url


class Base(DeclarativeBase):
    pass


engine = None
SessionLocal = sessionmaker()


def connect() -> None:
    global engine
    engine = create_engine(database_url(), pool_pre_ping=True, pool_size=5)
    SessionLocal.configure(bind=engine)
