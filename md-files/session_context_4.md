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
- cache.py created with Redis connection using env variable ✅
- Redis connection working (r.ping() returns True) ✅
- add_to_buffer() function written in cache.py ✅
- PATCH endpoint updated to write to Redis instead of Postgres ✅
- Postgres write code moved to write_to_postgres() function ✅
- drain_worker() function written in cache.py ✅
- lifespan function completed in main.py ✅
- End to end flow working: PATCH → Redis → drain worker → Postgres ✅
- None guard added to drain_worker ✅
- FastAPI tests written in test_main.py ✅
- Django test written in registrants/tests.py ✅
- GitHub Actions CI pipeline set up in .github/workflows/ci.yml ✅

## Key Files

- fastAPI/cache.py — Redis connection + add_to_buffer() + drain_worker()
- fastAPI/database.py — Postgres connection using psycopg2
- fastAPI/main.py — FastAPI app, PATCH endpoint, lifespan, write_to_postgres()
- fastAPI/test_main.py — FastAPI tests using TestClient and unittest.mock
- cc_registrant_dashboard/registrants/tests.py — Django tests
- cc_registrant_dashboard/pytest.ini — pytest config for Django
- .github/workflows/ci.yml — GitHub Actions CI pipeline
- docker-compose.yml — runs Postgres and Redis in Docker
- .env — contains DB credentials and REDIS_HOST (not committed to repo)

## Current ci.yml

```yaml
name: run_tests
run-name: django/fastAPI testing
on: [push]
jobs:
  container-job:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_USER: postgres_reg_dashboard
          POSTGRES_PASSWORD: 123456
          POSTGRES_DB: db_reg_dashboard
        ports:
          - 5432:5432
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
    steps:
      - name: Check out repository code
        uses: actions/checkout@v5
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: test fastAPI
        run: pytest
      - name: Connect to PostgreSQL and test django
        env:
          POSTGRES_HOST: localhost
          POSTGRES_PORT: 5432
          POSTGRES_USER: postgres_reg_dashboard
          POSTGRES_PASSWORD: 123456
          POSTGRES_DB: db_reg_dashboard
        run: cd cc_registrant_dashboard && pytest
```

## What's Next

1. Confirm CI pipeline is fully green (Django test passing in GitHub Actions)
2. WebSockets — replace Django's 1s polling with a persistent WebSocket connection for real time dashboard updates. Django needs Django Channels for WebSocket support.

## Key Testing Concepts Learned

- TestClient wraps the FastAPI app so you can send requests without running a server
- @patch("module.function") replaces a function with a mock — mock it where it's used, not where it's defined
- MagicMock() handles chained calls like conn.cursor().execute() automatically
- assert_called_once_with(...) checks exact arguments — "Expected" = your assertion, "Actual" = what really happened
- Django tests need Postgres running — Django creates a separate test db, runs tests, destroys it
- In GitHub Actions, service containers spin up the DB but the step still needs env vars to connect
- pytest must be run from inside the Django app directory, or use two separate steps in CI
- @pytest.mark.django_db required for any Django test that touches the database

## Key Concepts Learned

- Redis is an in-memory key-value store — RAM based, ~100x faster than Postgres
- Redis uses lpush to add to a list, rpop to remove — gives FIFO ordering
- async def makes a function a coroutine — required for asyncio.create_task
- asyncio.create_task runs a coroutine in the background without blocking
- asyncio.sleep vs time.sleep — time.sleep blocks the entire process
- lifespan is the modern replacement for @app.on_event("startup") in FastAPI
- The drain worker decouples incoming requests from Postgres writes
- Pass write_to_postgres as a parameter to drain_worker to avoid circular imports
- GitHub Actions service containers need credentials passed explicitly to each step that uses them

## Teaching Style That Works

- Don't give answers — ask questions and point to docs
- Let the student figure things out and explain them back
- Only move forward when they can explain it themselves
- They learn better from running code and getting real errors than from reading
- Pseudocode and plain English first, then real code
- They want to feel ownership over the work
- Don't be commanding — it's frustrating
