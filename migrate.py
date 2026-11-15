"""Run the Alembic migrations at start-up. Safe on every start: Alembic remembers what already ran (table
alembic_version); a Postgres advisory lock makes a second copy of the app wait instead of migrating twice."""
import logging
from pathlib import Path

from alembic import command
from alembic.config import Config
from sqlalchemy import text

import database

MIGRATION_LOCK = 4208
HERE = Path(__file__).resolve().parent


def run_migrations() -> None:
    cfg = Config(str(HERE / "alembic.ini"))
    cfg.set_main_option("script_location", str(HERE / "alembic"))
    with database.engine.begin() as connection:
        connection.execute(text("SELECT pg_advisory_xact_lock(:k)"), {"k": MIGRATION_LOCK})
        cfg.attributes["connection"] = connection      # env.py uses this connection (and so the lock)
        command.upgrade(cfg, "head")
    logging.getLogger("app").info("Database is up to date.")
