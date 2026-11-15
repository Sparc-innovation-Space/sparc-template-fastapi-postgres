"""Alembic environment: uses the app's connection when the app runs the migrations (migrate.py), otherwise
(`alembic upgrade head` / `alembic revision --autogenerate` on your computer) a new connection to DATABASE_URL."""
import sys
from pathlib import Path

from alembic import context
from sqlalchemy import create_engine

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import database  # noqa: E402
import models  # noqa: E402,F401  (registers the tables for --autogenerate)

target_metadata = database.Base.metadata


def run() -> None:
    connection = context.config.attributes.get("connection")
    if connection is not None:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()
        return
    engine = create_engine(database.database_url())
    with engine.connect() as conn:
        context.configure(connection=conn, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()


run()
