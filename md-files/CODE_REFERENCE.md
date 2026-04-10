# Code Reference — CrowdComms Project
======================================

Use this when you're genuinely stuck — not as a first resort.
Each example has an explanation of what it's doing and why.

---

## FastAPI — psycopg2 Cursor Pattern

```python
conn = get_db()          # opens a connection to Postgres
cursor = conn.cursor()   # creates a cursor — this is what runs your SQL
cursor.execute(
    "UPDATE registrants_registrant SET current_status = %s WHERE id = %s",
    (new_status, registrant_id)   # values are passed as a tuple, NOT in the string
)
conn.commit()    # makes the change permanent — without this it gets rolled back
cursor.close()   # close the cursor first
conn.close()     # then close the connection
```

**Why `%s` instead of an f-string?**
If you did `f"...status = '{new_status}'"`, a malicious client could send a value like
`"'; DROP TABLE registrants_registrant; --"` and destroy your data. psycopg2's `%s`
escapes the value safely before it touches the DB.

**Why commit?**
Postgres wraps every operation in a transaction. Until you commit, the change exists in
memory but isn't written to disk. If the connection closes without committing, Postgres
rolls it back automatically.

---

## Redis — Cache-Aside Pattern in a Django View

```python
from django.core.cache import cache
from django.db.models import Count

@api_view(['GET'])
def dashboard_summary(request, event_id):
    cache_key = f"dashboard_summary_{event_id}"   # unique key per event
    cached = cache.get(cache_key)

    if cached:
        return Response(cached)    # cache hit — skip the DB entirely

    # cache miss — run the query
    summary = (
        Registrant.objects
        .filter(event=event_id)
        .values('current_status')
        .annotate(count=Count('id'))
    )
    result = {item['current_status']: item['count'] for item in summary}

    cache.set(cache_key, result, timeout=30)   # store for 30 seconds
    return Response(result)
```

**What `.values().annotate()` does:**
`.values('current_status')` groups by that field. `.annotate(count=Count('id'))` adds
a count for each group. The result is like: `[{"current_status": "CHK", "count": 47}, ...]`
The dict comprehension on the next line turns it into `{"CHK": 47, "REG": 120, ...}`.

**Why a unique cache key per event?**
If you used a generic key like `"dashboard_summary"`, event 1 and event 2 would share
the same cache entry and overwrite each other.

---

## Django Settings — Redis Cache Configuration

```python
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://127.0.0.1:6379/1",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        }
    }
}
```

**What `/1` means at the end of the URL:**
Redis supports multiple logical databases (0–15), all on the same server. Using `/1`
for the cache keeps it separate from `/0` which Celery uses as the message broker.
Prevents them from interfering with each other.

---

## Celery — Setup Files

### `cc_registrant_dashboard/celery.py`

```python
import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'registrant_dashboard.settings')

app = Celery('registrant_dashboard')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()   # finds tasks.py in every installed app automatically
```

**Why `os.environ.setdefault` here?**
The Celery worker process starts independently of Django. It needs to know which settings
module to use. This line sets it if it hasn't been set already.

**Why `namespace='CELERY'`?**
Tells Celery to look for settings prefixed with `CELERY_` in `settings.py`
(e.g. `CELERY_BROKER_URL`). Keeps Celery config organised in one namespace.

### `cc_registrant_dashboard/__init__.py`

```python
from .celery import app as celery_app
__all__ = ('celery_app',)
```

**Why?**
This ensures the Celery app is loaded when Django starts, so the `@shared_task`
decorator works correctly across all apps.

---

## Celery — Task Definition

```python
# registrants/tasks.py
from celery import shared_task

@shared_task
def on_status_change(registrant_id, new_status):
    # This runs in the background worker, not in the web process
    print(f"Registrant {registrant_id} changed to {new_status}")
    # Real use: trigger badge printer, send SMS, call webhook, etc.
```

**Why `@shared_task` instead of `@app.task`?**
`@app.task` requires importing the Celery app directly — creates circular import issues
in Django. `@shared_task` binds to whatever app is configured at runtime. Always use
`@shared_task` in Django apps.

### Calling the task (fire-and-forget):

```python
on_status_change.delay(registrant_id, new_status)
```

`.delay()` puts the task on the Redis queue and returns immediately. The worker
picks it up in the background.

---

## pgvector — Django Model with VectorField

```python
from django.db import models
from pgvector.django import VectorField

class EventDocument(models.Model):
    event = models.ForeignKey('Event', on_delete=models.CASCADE)
    content = models.TextField()         # the raw text chunk
    embedding = VectorField(dimensions=1536)   # 1536 = OpenAI ada-002 output size
```

**Why `dimensions=1536`?**
OpenAI's `text-embedding-ada-002` model outputs a vector of 1536 floats. The dimension
must match exactly — if you use a different embedding model, the number changes.

---

## RAG — Embed and Store Documents

```python
import openai
from registrants.models import EventDocument, Event

def embed_text(text):
    response = openai.embeddings.create(
        input=text,
        model="text-embedding-ada-002"
    )
    return response.data[0].embedding   # returns a list of 1536 floats

# Called once to load your event data into the vector store
def load_event_documents(event_id, documents):
    event = Event.objects.get(pk=event_id)
    for text in documents:
        EventDocument.objects.create(
            event=event,
            content=text,
            embedding=embed_text(text)
        )
```

**What `embed_text` returns:**
A Python list of 1536 floats — the vector representation of the text. Similar texts
will produce similar lists. pgvector stores this and lets you query by distance.

---

## RAG — Query Endpoint

```python
from pgvector.django import L2Distance

@api_view(['POST'])
def ask_event(request, event_id):
    question = request.data['question']
    question_embedding = embed_text(question)   # embed the question too

    # Find the 3 most similar stored chunks
    docs = (
        EventDocument.objects
        .filter(event=event_id)
        .order_by(L2Distance('embedding', question_embedding))[:3]
    )

    context = "\n".join([doc.content for doc in docs])

    response = openai.chat.completions.create(
        model="gpt-4",
        messages=[{
            "role": "user",
            "content": f"Answer using this context:\n{context}\n\nQuestion: {question}"
        }]
    )
    return Response({"answer": response.choices[0].message.content})
```

**What `L2Distance` does:**
L2 (Euclidean) distance measures how far apart two vectors are. Ordering by it gives
you the chunks whose meaning is closest to the question. Smaller distance = more similar.

**Why inject context into the prompt?**
Without it, the LLM answers from its training data (which knows nothing about your
specific event). With the context injected, it answers from the retrieved chunks.
The LLM becomes a reasoning engine over your data, not a general knowledge base.

---

## Docker Compose — Adding Redis

```yaml
redis:
  image: redis:alpine
  ports:
    - "6379:6379"
```

Add this as a new service alongside your existing `db` service in `docker-compose.yml`.
`redis:alpine` is the lightweight version of the official Redis image.

---

## Dockerfiles

### Django

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["gunicorn", "registrant_dashboard.wsgi:application", "--bind", "0.0.0.0:8000"]
```

### FastAPI

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["fastapi", "run", "main.py", "--port", "8001"]
```

**Why gunicorn for Django?**
Django's development server (`manage.py runserver`) is not safe for production — single
threaded, no worker management. Gunicorn is a production-grade WSGI server.

**Why `0.0.0.0` instead of `127.0.0.1`?**
Inside a Docker container, `127.0.0.1` is the container's own loopback — nothing from
outside can reach it. `0.0.0.0` means "accept connections on all interfaces", so traffic
from outside the container (AWS load balancer, other containers) can reach it.

---

_This file exists for when you're genuinely stuck. If you haven't tried reading the
official docs first, do that first._
