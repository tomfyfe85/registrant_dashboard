# CrowdComms Project — Full Roadmap & Course Notes
=====================================================

A reference guide for finishing the registrant dashboard MVP end-to-end.
Each section covers what it is, why it exists, where to look in the docs, and interview questions.

**How to use this:** Read the concept. Go to the docs link. Build it yourself. Come back here
if you're genuinely stuck. The interview questions are how you'll know you've understood it.

---

## Table of Contents

1. [Project Overview & Architecture](#1-project-overview--architecture)
2. [Where You Are Now](#2-where-you-are-now)
3. [FastAPI — Database Connection & Check-in Endpoint](#3-fastapi--database-connection--check-in-endpoint)
4. [Redis — Caching](#4-redis--caching)
5. [Celery — Async Task Queue](#5-celery--async-task-queue)
6. [pgvector & RAG — AI Layer](#6-pgvector--rag--ai-layer)
7. [AWS Deployment](#7-aws-deployment)
8. [Tests](#8-tests)
9. [Full MVP Checklist](#9-full-mvp-checklist)

---

## 1. Project Overview & Architecture

### What You're Building

A registrant dashboard for live events. An organiser can see all attendees, their companies,
pass types, and real-time check-in status. The system handles a large volume of check-in
events arriving simultaneously when guests arrive at an event.

### Architecture

```
React Frontend (future)
        ↓
Django/DRF API          ← Admin CRUD, dashboard summary, registrant management
        ↓
FastAPI Service         ← High-frequency check-in status updates (async)
        ↓
PostgreSQL (Docker)     ← Single source of truth for all data
        ↑
Redis                   ← Cache dashboard counts, Celery message broker
        ↑
Celery Worker           ← Async tasks: badge printing, notifications, etc.
        ↑
pgvector (Postgres)     ← Vector search for RAG
        ↑
LLM (OpenAI/Claude)     ← Answers event questions from embedded data
```

### Why Each Piece

| Service   | Why it's here |
|-----------|---------------|
| Django    | CRUD, admin panel, migrations, auth — all the management-side features |
| DRF       | API layer on top of Django — serialization, validation, REST conventions |
| FastAPI   | Async check-in endpoint — handles volume spikes efficiently |
| Postgres  | Relational DB — registrants, events, companies, status history |
| Redis     | Cache dashboard counts so Django doesn't hit DB on every page load |
| Celery    | Offload slow tasks (badge printing, emails) so check-in isn't blocked |
| pgvector  | Store embeddings in Postgres — no separate vector DB needed |
| RAG       | Let organisers ask questions about their event data |
| AWS       | Host and scale the whole thing in production |

---

## 2. Where You Are Now

### Done ✅
- Django project scaffolded, `registrants` app created
- Docker + Postgres running with named volume
- All models complete and migrated: Event, Company, Registrant, StatusChange
- Full three-step data migration (CharField → ForeignKey for Company)
- All serializers: EventSerializer, RegistrantSerializer, StatusChangeSerializer
- DRF views complete:
  - `event_list` — GET all events
  - `create_registrant` — POST new registrant (auto-creates StatusChange)
  - `registrant_list` — GET all registrants for an event
  - `registrant_detail` — GET single registrant
  - `update_registrant` — PATCH any registrant field
  - `delete_registrant` — DELETE a registrant
- All URLs wired up and tested in Postman
- FastAPI installed and running on port 8001
- StatusUpdate Pydantic model with `current_status: str`
- `database.py` with `get_db()` connecting to Postgres via psycopg2

### In Progress 🔄
- FastAPI `update_status` endpoint — needs the SQL query to actually update the DB

### Still To Do
- FastAPI: execute UPDATE query, close connection, return response
- Redis: add to Docker, configure cache, use in dashboard_summary view
- Celery: setup, tasks.py, wire to status changes
- pgvector + RAG: event Q&A chatbot
- Tests
- AWS deployment

---

## 3. FastAPI — Database Connection & Check-in Endpoint

### Docs
- psycopg2 basic usage: https://www.psycopg.org/docs/usage.html
  - Read: **"Basic module usage"** — focus on `connect()`, cursors, `execute()`, `commit()`
  - Read: **"Passing parameters to SQL queries"** — the `%s` placeholder pattern
  - Skip: anything about `copy`, `NOTIFY`, async for now

### Key Concepts

**The cursor pattern:**
A psycopg2 connection object doesn't run queries directly. You create a cursor from it,
use the cursor to execute SQL, commit the change, then close both.

Look at the psycopg2 docs for the basic `connect()` → `cursor()` → `execute()` → `commit()` flow.

**Parameterised queries:**
Never build SQL strings with f-strings or `.format()` — that's a SQL injection vulnerability.
psycopg2 has a built-in safe way to pass values into queries. Find it in the docs under
"Passing parameters to SQL queries". It uses `%s` placeholders.

**Django's table naming convention:**
Django names DB tables as `{app_name}_{model_name}` in lowercase.
Your registrant table is `registrants_registrant`.

**Docker host note:**
When FastAPI runs locally (outside Docker), Postgres is reachable at `localhost`
because the Docker port mapping (`5432:5432`) exposes it to your machine.
When FastAPI is containerised later, you'd use the Docker service name instead.

### What to Build

In `main.py`, your `update_status` endpoint needs to:
1. Call `get_db()` to open a connection
2. Create a cursor
3. Execute an UPDATE query using parameterised values (registrant_id and new status)
4. Commit the change
5. Close cursor and connection
6. Return a response

Figure out the SQL UPDATE statement syntax yourself — it's standard SQL, not FastAPI-specific.

### Interview Questions — FastAPI & psycopg2

**Q: Why use psycopg2 in FastAPI instead of Django's ORM?**
FastAPI has no built-in ORM. Django's ORM is tightly coupled to Django's settings and
app registry — you can't just import a Django model into a separate service. psycopg2
lets you write raw SQL and talk to Postgres directly, without any framework dependency.

**Q: What is a database cursor?**
A cursor is an object that manages the execution of SQL statements. You create one from
a connection, use it to execute queries and fetch results, then close it. The connection
stays open until you close it explicitly.

**Q: What is a parameterised query and why does it matter?**
A parameterised query uses placeholders for values instead of string formatting.
psycopg2 fills them in safely, preventing SQL injection. Never build SQL strings with
f-strings or `.format()`.

**Q: Why do you need to commit after an UPDATE?**
Postgres uses transactions. Changes aren't permanent until you commit them. Without
committing, the UPDATE runs but gets rolled back when the connection closes.

---

## 4. Redis — Caching

### Docs
- Django cache framework: https://docs.djangoproject.com/en/stable/topics/cache/
  - Read: **"Setting up the cache"** and **"The low-level cache API"**
  - Focus on: `cache.get()`, `cache.set()`, `cache.delete()`
  - Skip: per-site cache, template fragment caching — those are frontend concerns
- django-redis: https://github.com/jazzband/django-redis (README is sufficient)

### CONCEPT: What Is Redis?

Redis is an in-memory data store. It holds data in RAM instead of on disk — reads and
writes are microseconds vs milliseconds for a DB query.

In this project Redis does two jobs:
1. **Cache** — stores the dashboard summary counts so Django doesn't query Postgres every time
2. **Message broker** — Celery uses it to pass task messages to workers

### Why Cache the Dashboard?

The dashboard summary (count per status, total registrants) needs a DB aggregation query.
If 50 browser tabs have the dashboard open, that's 50 queries per refresh.

With Redis: the first request hits the DB and stores the result. The next 49 requests get
the cached result instantly. After a TTL (time-to-live) expires, the cache refreshes.

### Setup

**Docker:** Add a Redis service to `docker-compose.yml` — look up the official Redis Docker image.

**Install:** `pip install redis django-redis`

**Configure:** In `settings.py`, add a `CACHES` block pointing at Redis.
The django-redis README shows the exact configuration format.

### The Cache Pattern

The `dashboard_summary` view should:
1. Build a cache key specific to the event (e.g. `dashboard_summary_{event_id}`)
2. Try `cache.get(key)` — if it returns something, return it immediately
3. If nothing cached (cache miss): run the DB query, build the result
4. Store the result with `cache.set(key, result, timeout=30)`
5. Return the result

This is the standard cache-aside pattern. Learn it — you'll use it everywhere.

### Cache Invalidation

When a status changes, the cached count is stale. Options:
1. **Short TTL** — cache expires every 30 seconds, eventually consistent (fine for MVP)
2. **Explicit invalidation** — `cache.delete(key)` on every status change (more correct)

For MVP: short TTL is fine.

### Interview Questions — Redis

**Q: What is Redis and why is it faster than Postgres for reads?**
Redis stores data in RAM. Postgres reads from disk (with its own cache layer). RAM access
is orders of magnitude faster. Redis is ideal for frequently-read data that doesn't change often.

**Q: What is a TTL in caching?**
Time-to-live — how long a cached value stays valid before expiring. After it expires, the
next request rebuilds the cache from the DB. Balances freshness vs performance.

**Q: What is cache invalidation and why is it hard?**
Knowing when to remove or update a cached value when the underlying data changes. If you
cache registrant counts and a new check-in happens, the cache is stale. You either set a
short TTL (accept brief staleness) or explicitly invalidate on every write (more complex).

**Q: What else does Redis do besides caching in this project?**
It acts as Celery's message broker — Celery workers listen on Redis queues and pick up tasks.

---

## 5. Celery — Async Task Queue

### Docs
- First steps with Celery: https://docs.celeryq.dev/en/stable/getting-started/first-steps-with-celery.html
- Django integration: https://docs.celeryq.dev/en/stable/django/first-steps-with-django.html
  - Read both pages in full — they're short and the setup has a specific structure

### CONCEPT: What Is Celery?

Celery is a distributed task queue. It lets you offload slow work to background workers
so your API response isn't blocked waiting for it.

**The problem:**
When a registrant checks in, you might want to trigger a badge printer or send a notification.
Doing this inside the endpoint means it takes 3 seconds. With Celery, you hand the work off
and respond immediately. The worker handles it in the background.

**Three components:**
- **Task** — a Python function decorated with `@shared_task`
- **Broker** — Redis (carries messages from app to workers)
- **Worker** — a separate process that listens for tasks and runs them

**The flow:**
```
Endpoint receives check-in
        ↓
task.delay(args)   ← puts a message on Redis
        ↓
Returns 200 immediately
        ↓ (meanwhile...)
Celery worker picks up message from Redis
        ↓
Runs the task function
```

### What to Build

1. Create `cc_registrant_dashboard/celery.py` — the Celery app setup (see Django docs)
2. Add Celery config to `settings.py` — broker URL pointing at Redis
3. Create `registrants/tasks.py` — one task: `on_status_change(registrant_id, new_status)`
4. Call `on_status_change.delay(...)` from `update_registrant` and the FastAPI endpoint
5. Run the worker: `celery -A registrant_dashboard worker --loglevel=info`
6. Trigger a status change and confirm the task fires in the worker terminal

### Interview Questions — Celery

**Q: What is Celery and why would you use it?**
Celery is a distributed task queue. You use it to offload work that's too slow for a
request/response cycle — sending emails, triggering printers, calling external APIs.
The endpoint responds immediately; Celery handles the rest asynchronously.

**Q: What is a message broker and why does Celery need one?**
The broker is the middleman between your app and Celery workers. Your app puts a task
message on the broker (Redis); the worker picks it up and executes it. Without it,
there's no way to pass work between processes.

**Q: What is the difference between `.delay()` and `.apply_async()`?**
Both send a task to the queue. `.delay()` is shorthand with no extra options.
`.apply_async()` lets you set countdown timers, ETAs, retries, etc. Use `.delay()` for
simple fire-and-forget.

**Q: What happens if a Celery task fails?**
By default it fails silently. You can configure retries with `max_retries` on the decorator
and use `self.retry()` inside the task. Flower (a web UI for Celery) lets you monitor failures.

---

## 6. pgvector & RAG — AI Layer

### Docs
- pgvector GitHub: https://github.com/pgvector/pgvector
- pgvector Python: https://github.com/pgvector/pgvector-python (see Django section)
- OpenAI Embeddings: https://platform.openai.com/docs/guides/embeddings
  - Read: what embeddings are, how to create one, what `text-embedding-ada-002` returns

### CONCEPT: What Are Embeddings?

An embedding converts text into a list of numbers (a vector) that represents its meaning.
Similar texts produce similar vectors. This enables semantic search — finding content by
meaning rather than keyword matching.

Example: "Guest arriving at venue" and "Person checking into event" will produce
similar vectors even though they share no keywords.

### CONCEPT: What Is pgvector?

A Postgres extension that adds a `vector` data type and similarity search operators.
This means you can store embeddings directly in your existing Postgres database and
query them by similarity — no separate vector database needed.

To use it: enable the extension in Postgres, install `pgvector` for Python,
add a `VectorField` to a Django model.

### CONCEPT: What Is RAG?

Retrieval-Augmented Generation. A pattern for making LLMs answer questions about your
specific data rather than their training data:

```
User question
        ↓
Embed the question (convert to vector)
        ↓
Query pgvector: find the most similar stored text chunks
        ↓
Build a prompt: "Using this context: [chunks], answer: [question]"
        ↓
Send to LLM (OpenAI/Claude)
        ↓
Return answer
```

### What to Build

1. Enable pgvector in Postgres (SQL extension command — in GitHub README)
2. Install: `pip install pgvector openai`
3. Create `EventDocument` model with a `VectorField` — stores chunks of event text + their embeddings
4. Write a management command (or view) to embed and store event documents
5. Create a `POST /events/{event_id}/ask/` endpoint that:
   - Embeds the question
   - Queries pgvector for similar chunks
   - Sends chunks + question to an LLM
   - Returns the answer

**What to embed:** Event schedule, speaker bios, venue info, FAQs.

### Interview Questions — RAG & pgvector

**Q: What is an embedding?**
A numerical representation of text as a high-dimensional vector. Similar texts produce
similar vectors. Enables semantic search — finding relevant content by meaning.

**Q: What is pgvector?**
A Postgres extension adding a `vector` data type and similarity search operators. Lets
you store and query embeddings in your existing Postgres database without a separate
vector store.

**Q: What is RAG?**
Retrieval-Augmented Generation. You embed a user's question, retrieve similar chunks from
your vector store, inject them into a prompt, and send to an LLM. The LLM answers using
your specific data rather than its training data.

**Q: Why RAG instead of fine-tuning?**
Fine-tuning bakes knowledge into the model at training time — expensive, slow, and you
must retrain when data changes. RAG retrieves fresh data at query time — cheaper, faster
to update, and the LLM stays general-purpose.

---

## 7. AWS Deployment

### Docs
- AWS Free Tier: https://aws.amazon.com/free/ (use this to keep costs near zero)
- ECS Getting Started: https://docs.aws.amazon.com/AmazonECS/latest/developerguide/getting-started.html
- GitHub Actions: https://docs.github.com/en/actions/quickstart

### CONCEPT: What Is ECS?

Elastic Container Service — AWS's managed service for running Docker containers.
You push your Docker image to ECR (AWS's container registry), and ECS runs it.
It handles restarts, scaling, and load balancing.

Key terms:
- **Task Definition** — the recipe (image, CPU, memory, env vars)
- **Service** — keeps your task running (restarts on crash, scales horizontally)
- **Cluster** — the collection of services
- **Fargate** — serverless ECS mode (no EC2 instances to manage)

### What Goes Where

| Component      | AWS Service |
|----------------|-------------|
| Django/DRF     | ECS (Fargate) |
| FastAPI        | ECS (Fargate, separate service) |
| Postgres       | RDS (managed Postgres) |
| Redis          | ElastiCache (managed Redis) |
| Static files   | S3 + CloudFront CDN |
| Secrets        | AWS Secrets Manager |

### CI/CD with GitHub Actions

Every push to `main` should:
1. Run tests
2. Build Docker image
3. Push to ECR
4. Update ECS service to use new image

GitHub Actions does this via a YAML workflow file in `.github/workflows/`.

### Deployment Order (when you're ready)

1. Create RDS Postgres instance — get connection string
2. Create ElastiCache Redis instance — get connection string
3. Create S3 bucket + CloudFront distribution for static files
4. Store secrets in AWS Secrets Manager
5. Write Dockerfiles for Django and FastAPI
6. Create ECR repositories, push images
7. Create ECS task definitions and services
8. Set up GitHub Actions workflow

### Interview Questions — AWS

**Q: What is ECS and how does it relate to Docker?**
ECS is AWS's managed container service. You build a Docker image, push it to ECR, and
ECS runs it in the cloud — handling restarts, scaling, load balancing. Fargate mode
means no servers to manage at all.

**Q: What is CloudFront and why use it with S3?**
CloudFront is a CDN. S3 stores your static files; CloudFront serves them from servers
near the user worldwide. Faster load times globally, reduced S3 costs.

**Q: What is CI/CD?**
Continuous Integration / Continuous Deployment. Tests run automatically on every push
(CI). If they pass, code deploys to production automatically (CD). GitHub Actions
defines the pipeline in a YAML file in your repo.

**Q: What is the difference between ECS and EC2?**
EC2 gives you a raw virtual machine — you manage the OS, Docker, everything. ECS
abstracts that away — you think in containers, not servers. Fargate removes even
the server management entirely.

---

## 8. Tests

### Docs
- pytest-django: https://pytest-django.readthedocs.io/
- DRF testing: https://www.django-rest-framework.org/api-guide/testing/
  - Focus on: `APIClient`, making requests, asserting status codes and response data

### Priority Order

Write these — in this order:
1. `test_registrant_list` — GET returns only registrants for the right event
2. `test_update_registrant` — PATCH updates the field, returns 200
3. `test_delete_registrant` — DELETE removes registrant, returns 204
4. `test_registrant_detail_not_found` — GET non-existent ID returns 404
5. `test_fastapi_update_status` — PATCH check-in endpoint updates DB

### Pattern Reminder

Each test: create the data you need → perform the action → assert the outcome.
Use `@pytest.mark.django_db` for any test touching the ORM.
Use `APIClient` from `rest_framework.test` to make HTTP requests.

---

## 9. Full MVP Checklist

### Django/DRF ✅
- [x] Event, Company, Registrant, StatusChange models
- [x] All serializers
- [x] All CRUD views
- [x] All URLs wired up
- [ ] `dashboard_summary` view (counts by status per event) + cached with Redis
- [ ] Error handling (try/except DoesNotExist → 404) on detail/update/delete views
- [ ] Tests for all views

### FastAPI 🔄
- [x] Running on port 8001
- [x] StatusUpdate Pydantic model
- [x] database.py with get_db()
- [ ] Execute UPDATE query in update_status
- [ ] Also create StatusChange record (raw SQL)
- [ ] Fire Celery task on status change

### Redis
- [ ] Add to docker-compose
- [ ] Configure Django cache backend
- [ ] Cache dashboard_summary
- [ ] Cache invalidation strategy

### Celery
- [ ] celery.py setup
- [ ] tasks.py with on_status_change task
- [ ] Wire to update_registrant and FastAPI endpoint
- [ ] Confirm worker fires in terminal

### pgvector & RAG
- [ ] Enable pgvector in Postgres
- [ ] EventDocument model with VectorField
- [ ] Embed and store sample documents
- [ ] ask_event endpoint

### AWS
- [ ] Dockerfile for Django
- [ ] Dockerfile for FastAPI
- [ ] RDS + ElastiCache provisioned
- [ ] ECS services running
- [ ] GitHub Actions CI/CD pipeline

---

_Use this as a map, not a manual. Build each section from the official docs.
The interview questions are how you'll know you've understood it._
