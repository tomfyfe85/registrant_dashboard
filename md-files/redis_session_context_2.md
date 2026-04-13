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

## Key Files
- `fastAPI/cache.py` — Redis connection + `add_to_buffer()` function
- `fastAPI/database.py` — Postgres connection using psycopg2
- `fastAPI/main.py` — FastAPI app, PATCH endpoint calls `add_to_buffer()`
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

def add_to_buffer(registrant_id, status):
    data = {"registrant_id": registrant_id, "status": status}
    json_data = json.dumps(data)
    r.lpush("status_update_que", json_data)
```

## Current PATCH Endpoint
```python
@app.patch("/registrant/registrant_id/{registrant_id}")
async def update_status(registrant_id: int, status_update: StatusUpdate):
    status = status_update.current_status
    add_to_buffer(registrant_id, status)
    return {"status": "queued", "registrant_id": registrant_id}
```

## Postgres Write Function (to be used by drain worker)
```python
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

## What's Next
- **Step 4** — Build the drain worker: a background asyncio task that:
  1. Wakes up every 0.5s
  2. Pops items from the Redis list (`rpop`)
  3. Writes to Postgres
  4. Registered on FastAPI startup using `lifespan`

## Key Concepts Learned
- Redis is an in-memory key-value store — RAM based, ~100x faster than Postgres
- Redis uses `lpush` to add to a list, `rpop` to remove — gives FIFO ordering
- Docker service names act as hostnames inside Docker network (`redis`) but from local machine use `127.0.0.1`
- `decode_responses=True` converts Redis bytes responses to Python strings automatically
- Buffering vs caching: buffering holds new data temporarily before its final destination; caching stores a copy of existing data for faster reads
- `json.dumps()` converts a Python dict to a JSON string for storage in Redis
- `json.loads()` converts it back to a dict when reading from Redis
- `*args` in a function signature means zero or more positional arguments — you don't write `*` when calling it
- When docs are confusing, search for examples — "redis-py lpush example"

## Teaching Style That Works For Me
- Don't give me answers — ask me questions and point me to docs
- Let me figure things out and explain them back
- Only move forward when I can explain it myself
- I want to feel ownership over the work
- I learn better from concrete examples than abstract signatures
