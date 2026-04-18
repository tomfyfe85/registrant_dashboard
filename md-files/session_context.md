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

## Key Files
- `fastAPI/cache.py` — Redis connection + `add_to_buffer()` + `drain_worker()`
- `fastAPI/database.py` — Postgres connection using psycopg2
- `fastAPI/main.py` — FastAPI app, PATCH endpoint, `lifespan`, `write_to_postgres()`
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
        status_change_item = json.loads(queue_item)  # BUG: crashes if queue_item is None
        write_function(status_change_item["registrant_id"], status_change_item["status"])
        await asyncio.sleep(0.5)
```

## Current `main.py` (relevant parts)
```python
from cache import add_to_buffer, drain_worker

app = FastAPI()

@asynccontextmanager
async def lifespan(app: FastAPI):
    asyncio.create_task(drain_worker(write_to_postgres))
    yield

@app.patch("/registrant/registrant_id/{registrant_id}")
async def update_status(registrant_id: int, status_update: StatusUpdate):
    status = status_update.current_status
    add_to_buffer(registrant_id, status)
    return {"status": "queued", "registrant_id": registrant_id}

def write_to_postgres(registrant_id: int, status_update: StatusUpdate):
    status = status_update.current_status
    conn = get_db()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("UPDATE registrants_registrant SET current_status = %s WHERE id = %s RETURNING *", (status, registrant_id))
    row = cur.fetchone()
    conn.commit()
    cur.close()
    conn.close()
    updated_registrant = Registrant(**row)
```

## Known Bug to Fix First
`drain_worker` crashes with `TypeError: the JSON object must be str, bytes or bytearray, not NoneType` when the Redis queue is empty — because `rpop` returns `None` and `json.loads(None)` fails.

Fix: add a `None` check before `json.loads`. If `queue_item is None`, skip the rest of the iteration.

```python
if queue_item is None:
    # skip — nothing in the queue this iteration
```

The student already knows the fix — just needs to implement it.

## What's Next
1. **Fix the None bug** in `drain_worker` ← do this first
2. **Tests** — pytest for the FastAPI endpoints and drain worker logic. Student has been pointed to FastAPI testing docs: https://fastapi.tiangolo.com/tutorial/testing/ — look at `TestClient`
3. **WebSockets** — replace Django's 1s polling with a persistent WebSocket connection for real time dashboard updates

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
- In Python, no need for function prototypes — just define before you call
- Pass `write_to_postgres` as a parameter to `drain_worker` to avoid circular imports between `cache.py` and `main.py`
- The drain worker loop runs every 0.5s regardless of whether the queue has items — `rpop` returning `None` doesn't stop the loop

## Teaching Style That Works
- Don't give answers — ask questions and point to docs
- Let the student figure things out and explain them back
- Only move forward when they can explain it themselves
- They learn better from running code and getting real errors than from reading
- Pseudocode and plain English first, then real code
- They want to feel ownership over the work
