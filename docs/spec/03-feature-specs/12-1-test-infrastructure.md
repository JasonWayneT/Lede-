# Story 12.1: Test Infrastructure -- Conftest, Fixtures, and Test Database

Status: ready-for-dev

## Story

As a developer,
I want a test infrastructure with shared fixtures, a test database, and mock HandoffPacket builders,
so that writing new tests requires minimal boilerplate and no side effects on real data.

## Acceptance Criteria

1. **Given** running `uv run pytest`, **When** the test suite starts, **Then** a fresh in-memory SQLite database is created for the test session and torn down after

2. **Given** any test needing an AppConfig, **When** it uses the `config` fixture, **Then** it receives a test-mode config pointing at the test database and a temp data directory — no real data files are touched

3. **Given** any test needing a HandoffPacket, **When** it uses the `mock_packet` fixture, **Then** it receives a HandoffPacket pre-populated with realistic test data for all fields

4. **Given** any test needing an HTTP client, **When** it uses the `async_client` fixture, **Then** it receives an `httpx.AsyncClient` configured against the test FastAPI app

5. **Given** the test suite running, **When** all tests complete, **Then** no real keyring entries, Gmail API calls, or LLM calls are made — all external services are mocked

## Tasks / Subtasks

- [ ] Implement `tests/conftest.py` (AC: 1, 2, 3)
  - [ ] `@pytest.fixture(scope="session") async def test_db()`: create in-memory async SQLite engine, run `create_all`, yield, dispose
  - [ ] `@pytest.fixture async def config(tmp_path)`: return `AppConfig(data_dir=tmp_path, llm_provider="ollama", ...)`
  - [ ] `@pytest.fixture async def mock_packet()`: return `HandoffPacket(run_id=1, emails=[...], extracted_texts=[...], ...)` with realistic test data
  - [ ] Global mock patches for external services: `pytest.fixture(autouse=True)` that patches `keyring`, `googleapiclient`, `openai`, `anthropic`, `google.generativeai`

- [ ] Implement `tests/api/conftest.py` (AC: 4)
  - [ ] `@pytest.fixture async def async_client(test_db)`: `AsyncClient(app=app, base_url="http://test")` using `httpx.AsyncClient` with `transport=ASGITransport(app=app)`
  - [ ] Override DB dependency to use test DB

- [ ] Implement `tests/pipeline/conftest.py` (AC: 3)
  - [ ] Stage-specific mock HandoffPacket builders per stage
  - [ ] `mock_packet_for_embed()` — packet with extracted_texts populated
  - [ ] `mock_packet_for_cluster()` — packet with embeddings populated
  - [ ] etc. for each stage

- [ ] Configure `pytest.ini` or `pyproject.toml` (AC: 1)
  - [ ] `asyncio_mode = "auto"` for pytest-asyncio
  - [ ] `testpaths = ["tests"]`

- [ ] Write meta-test: `tests/test_infrastructure.py` (AC: 1–5)
  - [ ] Test that `config` fixture returns AppConfig with tmp_path as data_dir
  - [ ] Test that `mock_packet` fixture has all required HandoffPacket fields
  - [ ] Test that `async_client` fixture returns connected httpx client

## Dev Notes

### pytest-asyncio configuration

Add to `pyproject.toml`:
```toml
[tool.pytest.ini_options]
asyncio_mode = "auto"
testpaths = ["tests"]
```

And: `uv add --dev pytest-asyncio` (in addition to `pytest` and `httpx` from Story 1.1).

### In-memory SQLite for tests

```python
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

@pytest.fixture(scope="session")
async def engine():
    engine = create_async_engine(TEST_DATABASE_URL)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    await engine.dispose()
```

### Autouse mocks for external services

```python
@pytest.fixture(autouse=True)
def mock_keyring(monkeypatch):
    monkeypatch.setattr("keyring.get_password", lambda *a: None)
    monkeypatch.setattr("keyring.set_password", lambda *a: None)
    monkeypatch.setattr("keyring.delete_password", lambda *a: None)
```

This prevents any test from accidentally writing to the real OS keychain.

### httpx AsyncClient for FastAPI

```python
from httpx import AsyncClient, ASGITransport
from app.main import app

@pytest.fixture
async def async_client():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        yield client
```

### References

- [Source: docs/ARCHITECTURE.md § "Testing Standards"] — pytest + httpx AsyncClient, mock HandoffPacket fixtures
- [Source: docs/epics-stories.md § "Story 12.1"] — acceptance criteria

## Dev Agent Record

### Agent Model Used

claude-sonnet-4-6

### Debug Log References

### Completion Notes List

### File List
