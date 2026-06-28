# Story 1.3: Database Models and Async SQLite Initialization

Status: ready-for-dev

## Story

As a developer,
I want SQLAlchemy async models for Run, BriefingOutput, and ProcessedEmail created and the database initialized on app startup,
so that all features that read or write persistent data have a ready-to-use schema.

## Acceptance Criteria

1. **Given** the app starting for the first time, **When** the FastAPI lifespan event fires, **Then** `data/briefing.db` is created and all three tables exist: `runs`, `briefing_outputs`, `processed_emails`

2. **Given** the `runs` table, **When** I inspect its schema, **Then** columns exist: `id` (int PK autoincrement), `status` (str, default `"pending"`), `created_at` (datetime), `depth` (str), `section_config` (JSON), `error` (str nullable)

3. **Given** the `briefing_outputs` table, **When** I inspect its schema, **Then** columns exist: `id` (int PK), `run_id` (int FK runs.id), `markdown_path` (str), `audio_path` (str nullable)

4. **Given** the `processed_emails` table, **When** I inspect its schema, **Then** columns exist: `id` (int PK), `email_id` (str unique), `run_id` (int FK runs.id), `processed_at` (datetime)

5. **Given** the database module, **When** I call `get_session()`, **Then** it returns an async SQLAlchemy session compatible with `async with` context management

6. **Given** the app restarting when `briefing.db` already exists, **When** the lifespan event fires, **Then** no error is raised and existing data is preserved (`create_all` is idempotent)

## Tasks / Subtasks

- [ ] Implement async SQLite engine and session factory in `app/db/database.py` (AC: 1, 5, 6)
  - [ ] Create async engine: `create_async_engine("sqlite+aiosqlite:///data/briefing.db", echo=False)`
  - [ ] Create `AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)`
  - [ ] Implement `async def get_session()` as an async context manager yielding an `AsyncSession`
  - [ ] Implement `async def init_db()` that calls `async with engine.begin() as conn: await conn.run_sync(Base.metadata.create_all)`

- [ ] Implement SQLAlchemy models in `app/db/models.py` (AC: 2, 3, 4)
  - [ ] Define `Base = declarative_base()`
  - [ ] Model `Run`: table `runs`, columns per AC 2 — status default `"pending"`, `section_config` as `JSON` type, `error` nullable, `created_at` defaults to `datetime.utcnow`
  - [ ] Model `BriefingOutput`: table `briefing_outputs`, `audio_path` nullable string
  - [ ] Model `ProcessedEmail`: table `processed_emails`, `email_id` with `unique=True`, `processed_at` defaults to `datetime.utcnow`
  - [ ] Status enum values: `pending`, `running`, `complete`, `failed`, `hold`, `no_new_emails`
  - [ ] All column names: `snake_case` (no camelCase)

- [ ] Wire `init_db()` into FastAPI lifespan in `app/main.py` (AC: 1, 6)
  - [ ] Use `@asynccontextmanager` lifespan pattern (FastAPI 0.99+ pattern, not deprecated `on_event`)
  - [ ] Call `await init_db()` inside the lifespan startup block before `yield`

- [ ] Write tests (AC: 1–6)
  - [ ] `tests/api/conftest.py`: create in-memory SQLite engine for tests: `"sqlite+aiosqlite:///:memory:"`
  - [ ] Test that `init_db()` creates all three tables
  - [ ] Test that `init_db()` called twice does not error (idempotency)
  - [ ] Test `get_session()` returns usable async session

## Dev Notes

### Package versions

- `sqlalchemy` (async) and `aiosqlite` already installed via Story 1.1 `uv add`
- Use `sqlalchemy.ext.asyncio` — NOT the deprecated sync engine

### Lifespan pattern (FastAPI)

```python
from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.db.database import init_db

@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield

app = FastAPI(lifespan=lifespan)
```

### Column type for section_config

Use `sqlalchemy.types.JSON` — SQLite stores it as text and SQLAlchemy handles serialize/deserialize.

### DB path

The engine path must read from `AppConfig.data_dir` — do not hardcode `"data/briefing.db"`. The database module should accept a URL string and `database.py` should not instantiate `AppConfig` itself; the URL should be passed in or the engine initialized lazily at `init_db()` call time.

### Entry point isolation

`db/` may not import from `main.py`, `mcp_server.py`, or `api/`. It imports only SQLAlchemy and stdlib.

### References

- [Source: docs/ARCHITECTURE.md § "Data Architecture"] — three tables, no Alembic, `create_all` on startup
- [Source: docs/ARCHITECTURE.md § "Naming Patterns — Database Column Naming"] — snake_case, status enum values
- [Source: docs/epics-stories.md § "Story 1.3"] — acceptance criteria

## Dev Agent Record

### Agent Model Used

claude-sonnet-4-6

### Debug Log References

### Completion Notes List

- Implemented async SQLite DB layer with engine initialization (`init_engine`), schema creation (`init_db`), and async session context manager (`get_session`).
- Implemented models `Run`, `BriefingOutput`, `ProcessedEmail` with required columns and types (incl. JSON for `section_config`).
- Wired DB initialization into FastAPI lifespan in `briefing/app/main.py` using `AppConfig.data_dir` (no hardcoded `data/briefing.db`).
- Verification: `uv run pytest -q tests/test_db.py` (PASS).

### File List

- `briefing/app/db/models.py`
- `briefing/app/db/database.py`
- `briefing/app/main.py`
- `briefing/tests/test_db.py`
