# Session Context — Redis Buffer Project

## Who I am
I'm a junior developer trying to get my first full time tech role. I use Python, FastAPI, Django, and PostgreSQL. I'm learning AWS. I want to own my work and understand it — not just copy paste from AI. Treat me like a university lecturer would: point me to docs, ask me questions, don't give me answers directly.

## The Project
A registration dashboard for events. Registrants check in at events and their status changes (registered → checked_in etc). FastAPI handles the PATCH endpoint. Django polls PostgreSQL every 1 second to update the dashboard.

## The Problem We're Solving
PostgreSQL has a max connection limit (~100). If 500 people check in simultaneously, 500 connections hit Postgres at once — requests beyond the limit fail. Redis acts as a write buffer to absorb the burst.

## The Architecture (MVP)
```
PATCH /event → FastAPI → Redis (write buffer) → drain worker → PostgreSQL ← Django polls every 1s
```
Django does NOT need Redis — it just polls Postgres directly. Redis is a performance/resilience layer for the FastAPI write path only.

## What's Been Done
- PostgreSQL running in Docker ✅
- FastAPI PATCH endpoint working ✅
- Redis running in Docker ✅
- `cache.py` created with Redis connection using env variable ✅
- Redis connection working (`r.ping()` returns `True`) ✅
- `add_to_buffer()` function written in `cache.py` ✅
- PATCH endpoint updated to write to Redis instead of Postgres ✅
- Postgres write code moved to `write_to_postgres()` function ✅
- `drain_worker()` function written in `cache.py` ✅
- `lifespan` function completed in `main.py` ✅
- End to end flow working: PATCH → Redis → drain worker → Postgres ✅
- `None` guard added to `drain_worker` ✅
- FastAPI tests written in `test_main.py` ✅
- Django tests running (need Docker/Postgres up) ✅

## Key Files
- `fastAPI/cache.py` — Redis connection + `add_to_buffer()` + `drain_worker()`
- `fastAPI/database.py` — Postgres connection using psycopg2
- `fastAPI/main.py` — FastAPI app, PATCH endpoint, `lifespan`, `write_to_postgres()`
- `fastAPI/test_main.py` — FastAPI tests using TestClient and unittest.mock
- `docker-compose.yml` — runs Postgres and Redis in Docker
- `.env` — contains `REDIS_HOST=127.0.0.1`

## Current `cache.py`
```python
import redis
import json
from dotenv import load_dotenv
import os

load_dotenv()

REDIS_HOST = os.getenv("REDIS_HOST")

r = redis.Redis(host=REDIS_HOST, port=6379, decode_responses=True)

def add_to_buffer(registrant_id: int, status: str):
    data = {"registrant_id": registrant_id, "status": status}
    json_data = json.dumps(data)
    r.lpush("status_update_que", json_data)

async def drain_worker(write_function):
    while True:
        queue_item = r.rpop("status_update_que")
        if queue_item is None:
            await asyncio.sleep(0.5)
            continue
        status_change_item = json.loads(queue_item)
        write_function(status_change_item["registrant_id"], status_change_item["status"])
        await asyncio.sleep(0.5)
```

## Current `test_main.py`
```python
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from main import app, write_to_postgres

client = TestClient(app)

@patch("main.add_to_buffer")
def test_patch(mock_add_to_buffer):
    response = client.patch("/registrant/registrant_id/1", json={"current_status": "CHK"})
    assert response.status_code == 200

@patch("main.get_db")
def test_write_to_postgres(mock_get_db):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_get_db.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cursor
    mock_cursor.fetchone.return_value = {
        "id": 1, "name": "Tom", "email": "tom@test.com",
        "company_fk_id": 1, "event_id": 1,
        "guest_type": "guest", "current_status": "REG"
    }

    write_to_postgres(1, "CHK")

    mock_cursor.execute.assert_called_once_with(
        "UPDATE registrants_registrant SET current_status = %s WHERE id = %s RETURNING *",
        ("CHK", 1)
    )
    mock_conn.commit.assert_called_once()
```

## Key Testing Concepts Learned
- `TestClient` wraps the FastAPI app so you can send requests without running a server
- `@patch("module.function")` replaces a function with a mock for the duration of the test — mock it where it's used, not where it's defined
- The mock object is injected as the first parameter of the test function — name it anything descriptive
- `MagicMock()` handles chained calls like `conn.cursor().execute()` automatically
- `assert_called_once_with(...)` checks the mock was called with exact arguments
- In the error output: "Expected" = what your assertion said, "Actual" = what really happened
- Django tests need Postgres running — Django creates a separate test db, runs tests, destroys it
- FastAPI tests mock external dependencies (Redis, Postgres) for true isolation
- Unit tests: test one function in isolation. Integration tests: test how pieces work together, still mocking external services

## What's Next
1. **WebSockets** — replace Django's 1s polling with a persistent WebSocket connection for real time dashboard updates
2. **GitHub Actions pipeline** — CI/CD pipeline to run tests on push

## Key Concepts Learned
- Redis is an in-memory key-value store — RAM based, ~100x faster than Postgres
- Redis uses `lpush` to add to a list, `rpop` to remove — gives FIFO ordering
- `decode_responses=True` converts Redis bytes to Python strings automatically
- Buffering vs caching: buffering holds new data temporarily before its final destination; caching stores a copy of existing data for faster reads
- `json.dumps()` converts a Python dict to a JSON string for Redis storage
- `json.loads()` converts it back — but crashes on `None`, so always guard first
- `async def` makes a function a coroutine — required for `asyncio.create_task`
- `asyncio.create_task` runs a coroutine in the background without blocking
- `asyncio.sleep` vs `time.sleep` — `time.sleep` blocks the entire process; `asyncio.sleep` yields control back to the event loop
- `while True` with `asyncio.sleep` is the pattern for a continuously running background task
- `lifespan` is the modern replacement for `@app.on_event("startup")` in FastAPI
- The drain worker decouples incoming requests from Postgres writes — 1 worker draining calmly vs 500 simultaneous connections
- WebSockets and the drain worker solve different problems — drain worker moves data server-side, WebSockets push updates to the browser
- Pass `write_to_postgres` as a parameter to `drain_worker` to avoid circular imports between `cache.py` and `main.py`

## Teaching Style That Works
- Don't give answers — ask questions and point to docs
- Let the student figure things out and explain them back
- Only move forward when they can explain it themselves
- They learn better from running code and getting real errors than from reading
- Pseudocode and plain English first, then real code
- They want to feel ownership over the work
- Don't tell them what to do in a commanding way — it's frustrating
