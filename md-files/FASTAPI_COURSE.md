# FastAPI Course Notes — CrowdComms Project

---

## Pydantic & BaseModel
======================

CONCEPT: What Is Pydantic?
--------------------------
Pydantic is a Python library for data validation using type hints. You define a class that
describes the shape of your data — Pydantic enforces it automatically.

It's used heavily in FastAPI as the standard way to define request bodies and response shapes.

WHY IT EXISTS:
- Python is dynamically typed — nothing stops someone sending `{"current_status": 999}` when
  you expect a string
- Without validation, you'd have to manually check every field yourself
- Pydantic does this automatically, at the boundary where data enters your system

HOW IT WORKS:
1. You define a class inheriting from `BaseModel`
2. Each field is declared with a name and a type hint
3. When you instantiate the class with data, Pydantic validates it
4. If the data doesn't match, Pydantic raises a `ValidationError` with a clear message
5. In FastAPI, this happens automatically — invalid requests return a 422 response

```python
from pydantic import BaseModel

class StatusUpdate(BaseModel):
    current_status: str
```

When FastAPI receives a request body, it:
1. Parses the raw JSON
2. Passes it to your Pydantic model
3. Validates each field
4. Makes the validated object available in your function

KEY INSIGHT:
Pydantic is the Django serializer equivalent in FastAPI — it handles deserialization
and validation of incoming data. The difference is it's pure Python, not tied to a DB model.

MAIN USE CASES:
1. Request body validation in FastAPI endpoints
2. Response shape definition (what you send back to the client)
3. Any time you want to validate data coming into your system (config files, API responses, etc.)

COMPARISON — DRF vs FastAPI:
| DRF                        | FastAPI                    |
|----------------------------|----------------------------|
| Serializer                 | Pydantic BaseModel         |
| serializer.is_valid()      | Automatic (422 if invalid) |
| serializer.validated_data  | The model instance itself  |
| ModelSerializer            | No direct equivalent*      |

*FastAPI doesn't have a built-in ORM — you bring your own (SQLAlchemy, psycopg2, etc.)

---

## async / await
================

CONCEPT: What Is Async?
-----------------------
Asynchronous programming lets a function pause while waiting for something slow (DB query,
API call, file read) and let other code run in the meantime.

WHY IT EXISTS:
- In synchronous (normal) Python, one thing happens at a time
- If your function waits 200ms for a DB response, the whole thread is blocked
- At scale (hundreds of requests/second), this becomes a bottleneck
- Async lets the server handle other requests while waiting

HOW IT WORKS:
```python
async def update_status(registrant_id: int):
    result = await db.fetch(registrant_id)  # pauses here, doesn't block
    return result
```

- `async def` — marks a function as a coroutine (can be paused)
- `await` — pauses execution until the awaited thing completes

KEY INSIGHT:
Async doesn't make individual operations faster. It makes the server more efficient
under load — it can handle many concurrent requests with fewer threads.

WHEN TO USE:
- FastAPI endpoints (especially high-frequency ones like check-in)
- Any I/O-bound work: DB queries, external API calls, file reads
- NOT for CPU-bound work (image processing, ML inference) — use Celery for that

---

## Interview Questions

### Pydantic & BaseModel

**Q: What is Pydantic and why does FastAPI use it?**
Pydantic is a data validation library that uses Python type hints. FastAPI uses it to automatically validate incoming request data — if the data doesn't match the expected shape, FastAPI returns a 422 before your function code even runs.

**Q: What is BaseModel?**
A class provided by Pydantic. When your class inherits from it, Pydantic's validation logic gets baked in. You declare your fields and their types, and Pydantic handles the rest.

**Q: How is a Pydantic model different from a DRF serializer?**
Both validate incoming data, but a Pydantic model is pure Python — it has no knowledge of a database. A DRF serializer is tied to Django's ORM and can read/write model instances directly. In FastAPI you bring your own DB layer (SQLAlchemy, psycopg2 etc.).

**Q: What HTTP status code does FastAPI return if Pydantic validation fails?**
422 Unprocessable Entity — with a detailed error body explaining which field failed and why.

**Q: Do field names in a Pydantic model need to match the JSON keys in the request body?**
Yes — exactly. If the client sends `{"current_status": "CHK"}` but your model has `status: str`, Pydantic treats `status` as missing and returns a 422.

---

### Async / Await

**Q: What does `async def` mean in Python?**
It marks a function as a coroutine — a function that can be paused while waiting for I/O (DB queries, API calls) and resumed later. Other code can run during the pause.

**Q: Does async make individual operations faster?**
No. It makes the server more efficient under load. While one request is waiting for a DB response, the server can handle other incoming requests instead of blocking.

**Q: When would you use async vs Celery?**
Async for I/O-bound work (DB queries, API calls) — fast operations where you're just waiting. Celery for CPU-bound or long-running work (sending emails, generating reports, ML inference) — tasks you want to offload entirely and run in the background.

**Q: Why is FastAPI a good choice for a check-in endpoint at a large event?**
At peak times (everyone arriving at once), hundreds of requests hit the endpoint simultaneously. FastAPI's async nature means the server isn't blocked waiting for each DB update — it can handle many concurrent requests efficiently.

---

### FastAPI General

**Q: What is the difference between a path parameter and a request body in FastAPI?**
A path parameter is part of the URL (e.g. `/registrant/{registrant_id}`) and is a simple type (`int`, `str`). A request body is JSON sent in the request — FastAPI identifies it by the parameter being typed as a Pydantic model.

**Q: What is the `/docs` endpoint in FastAPI?**
Auto-generated interactive API documentation (Swagger UI). FastAPI builds it from your route definitions and Pydantic models automatically — no extra setup needed.

**Q: Why use FastAPI alongside Django rather than for everything?**
Django gives you the admin panel, ORM, migrations, and auth for free — ideal for the management/admin side of an application. FastAPI is better suited for high-frequency, low-latency endpoints where async performance matters. Using both means the right tool for the right job.
