# FastAPI + PostgreSQL — a SPARC Cloud template

A **Python API with FastAPI**, **SQLAlchemy** for the database and **Alembic** for database changes (migrations).
Interactive API documentation is built in at **`/docs`**. Needs a PostgreSQL database.

```
main.py              the app and its routes (start here)
models.py            your tables (SQLAlchemy)
database.py          the connection (DATABASE_URL)
migrate.py           runs the migrations at start-up (with a lock)
alembic/versions/    the database changes, in order
requirements.txt     exact versions of every package; .python-version = Python 3.13
sparc.json           tells SPARC Cloud how to run this (port, health check, database)
```

| Route | What it does |
| --- | --- |
| `GET /docs` | interactive documentation (try every route in the browser) |
| `GET /api/items`, `POST /api/items` `{"name": "…"}` | list / add items |
| `GET /healthz` | 200 when the database answers |

## Run it on your computer

```sh
python3 -m venv .venv && . .venv/bin/activate && pip install -r requirements.txt
docker run -d --name pg -e POSTGRES_USER=app -e POSTGRES_PASSWORD=app -e POSTGRES_DB=app -p 5432:5432 postgres:17-alpine
DATABASE_URL=postgresql://app:app@localhost:5432/app uvicorn main:app --reload --port 8080
# open http://localhost:8080/docs
```

## Deploy on SPARC Cloud

1. Dashboard → **Templates** → *FastAPI + PostgreSQL* → **Create my copy on GitHub** (your account/organization, a
   repository name). The copy is yours.
2. **I've created it** → pick the new repository (**Refresh** if needed).
3. Review: port 8080, health check `/healthz`, **a PostgreSQL database** (create one or use an existing one; needs a
   startup **owner**). **Create**.
4. SPARC Cloud builds it without a Dockerfile (start: `uvicorn main:app`), deploys it, and sets `DATABASE_URL`.

At every start the migrations run first. If they fail, the log says `MIGRATIONS FAILED …` and the new version never
becomes ready (the old one keeps running). The app runs as user 1000, not root.

## Change things

- **Add a route** in `main.py` (see the example at the bottom).
- **Add a table/column:** change `models.py`, then create a migration on your computer (with the local database
  running): `alembic revision --autogenerate -m "add price"` — check the new file in `alembic/versions/`, commit it.
  It runs on SPARC Cloud at the next start.
- Settings (`Settings & secrets` tab) arrive as environment variables: `os.environ["MY_SETTING"]`.
- **Update packages:** change the version in `requirements.txt` (exact `==` versions), test, commit.
- No telemetry: `opentelemetry-api` comes with FastAPI but is only the empty API (nothing is collected or sent).

## Licence

MIT (see `LICENSE`). The copy you made is yours.
