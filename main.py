"""A FastAPI app with PostgreSQL. Open /docs for the interactive API documentation.

SPARC Cloud starts it with:  uvicorn main:app --host 0.0.0.0 --port $PORT
At start-up the database migrations run first (alembic upgrade head). If they fail, the app stops with a clear
"MIGRATIONS FAILED" line in the log and never becomes ready.
"""
import logging
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, HTTPException
from fastapi.responses import PlainTextResponse
from pydantic import BaseModel, Field
from sqlalchemy import select, text
from sqlalchemy.orm import Session

import database
from migrate import run_migrations
from models import Item

log = logging.getLogger("app")
logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        database.connect()
        run_migrations()
    except Exception as e:  # noqa: BLE001 - one clear line, then stop
        log.error("MIGRATIONS FAILED - the app will not start: %s", e.__class__.__name__ + ": " + str(e)[:300])
        raise SystemExit(1) from None
    yield


app = FastAPI(title="My API", version="1.0.0", lifespan=lifespan)


def get_db():
    with database.SessionLocal() as session:
        yield session


@app.get("/healthz", response_class=PlainTextResponse, include_in_schema=False)
def healthz(db: Session = Depends(get_db)):
    """Health check for SPARC Cloud: 200 when the database answers."""
    try:
        db.execute(text("SELECT 1"))
    except Exception as e:  # noqa: BLE001
        log.warning("Health check: database not answering (%s)", e.__class__.__name__)
        raise HTTPException(status_code=503, detail="database not answering")
    return "ok"


@app.get("/")
def home():
    return {"name": "fastapi-postgres", "docs": "/docs", "routes": ["GET /api/items", "POST /api/items"]}


class NewItem(BaseModel):
    name: str = Field(min_length=1, max_length=200)


@app.get("/api/items")
def list_items(db: Session = Depends(get_db)):
    rows = db.scalars(select(Item).order_by(Item.id.desc()).limit(100))
    return [{"id": i.id, "name": i.name, "created_at": i.created_at} for i in rows]


@app.post("/api/items", status_code=201)
def create_item(body: NewItem, db: Session = Depends(get_db)):
    item = Item(name=body.name)
    db.add(item)
    db.commit()
    db.refresh(item)
    return {"id": item.id, "name": item.name, "created_at": item.created_at}

# Add your own routes here, e.g.
# @app.get("/api/hello")
# def hello(): return {"hello": "world"}
