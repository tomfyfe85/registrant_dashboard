# Django REST Framework Course - TaxConductor Edition
=====================================================

A textbook-style reference guide built alongside the TaxConductor project.
Each concept includes: theory, examples, and implementation options.

---

## Table of Contents
1. [Serializers](#serializers)
2. [Views & ViewSets](#views--viewsets)
3. [Authentication & Permissions](#authentication--permissions) (Coming soon)
4. [Advanced Topics](#advanced-topics) (Coming soon)

---

## Serializers

### What is a Serializer?

**Definition:**
A serializer is a translator between two languages:
- **Python objects** (Django models, QuerySets, dictionaries) ↔ **JSON** (or XML, or other formats)

Think of it like an interpreter at the UN:
- When data comes IN (client → server): JSON → Python objects (deserialization)
- When data goes OUT (server → client): Python objects → JSON (serialization)

### Why Do We Need Serializers?

**The Problem:**
You already solved part of this manually! Remember in your `all_transactions` view:

```python
transactions = list(Transaction.objects.all().values())
return JsonResponse(transactions, safe=False)
```

You had to:
1. Call `.values()` to convert QuerySet → dictionaries
2. Wrap it in `list()` to make it JSON-serializable
3. Use `JsonResponse` to convert to JSON

**What's missing?**
- ❌ No validation when creating/updating data
- ❌ Manual handling of relationships (ForeignKeys)
- ❌ No customization of which fields to show/hide
- ❌ No way to handle nested data (e.g., include category details)
- ❌ Manual error handling for bad data
- ❌ Code duplication for every endpoint

**The Solution:**
Serializers do ALL of this in one reusable class.

### How Serializers Work

**Two Main Jobs:**

#### 1. SERIALIZATION (Python → JSON)
```
Django Model Object
    ↓
Serializer reads the model
    ↓
Converts to Python dict
    ↓
DRF converts to JSON
    ↓
Client receives JSON
```

#### 2. DESERIALIZATION (JSON → Python)
```
Client sends JSON
    ↓
DRF parses to Python dict
    ↓
Serializer validates the data
    ↓
If valid: creates/updates model
If invalid: returns errors
```

### Analogy: The Factory Assembly Line

Think of a serializer like a factory that makes and unpacks boxes:

**Packing (Serialization):**
- Input: A real product (Django model)
- Process: Put it in a box with a label (JSON structure)
- Output: Shipping-ready package (JSON response)

**Unpacking (Deserialization):**
- Input: A box arrives (JSON from client)
- Quality Control: Check contents are correct (validation)
- If pass: Unpack and put on shelf (save to database)
- If fail: Return to sender with error note (validation errors)

### Types of Serializers

**1. Serializer (base class)**
- You define every field manually
- Full control, but verbose
- Use when: custom data structures that don't match a model

**2. ModelSerializer (most common)**
- Automatically generates fields from a Django model
- Less code, follows DRY principle
- Use when: your API closely matches your database model

**3. HyperlinkedModelSerializer**
- Like ModelSerializer but uses URLs instead of IDs for relationships
- More RESTful, better for browseable APIs
- Use when: you want clients to navigate your API through links

---

### Key Concepts

**Fields:**
Each serializer has fields (like Django model fields):
- `CharField`, `IntegerField`, `DecimalField`, etc.
- Each field knows how to:
  - Read from a Python object
  - Write to JSON
  - Validate incoming data

**Validation:**
Serializers validate data in THREE layers:
1. **Field-level:** Each field checks its own type (e.g., is this really a decimal?)
2. **Custom field validation:** `validate_<field_name>()` methods
3. **Object-level:** `validate()` method checks relationships between fields

**Read-only vs Write-only:**
- `read_only=True`: Show in responses, but ignore if client sends it
  - Example: `id`, `created_at` (we generate these, client can't set them)
- `write_only=True`: Accept from client, but don't show in responses
  - Example: `password` (we need it to create user, but don't send it back)

---

### Coming Up Next

Once you understand serializers, you'll learn:
- **Views with serializers:** How to use serializers in your view functions
- **Generic views:** DRF's pre-built views that handle common patterns
- **ViewSets:** Even more powerful - one class handles all CRUD operations
- **Routers:** Automatically create URLs for your ViewSets

---

*Last updated: 2026-03-12*

---

## Views & ViewSets

Views
=====

CONCEPT: What Is It?
--------------------
A view is the function (or class) that handles an HTTP request and returns an HTTP response.

When a request comes in:
1. Django checks the URL patterns in `urls.py`
2. Finds the matching view function
3. Calls it with the request object (and any URL parameters)
4. The view does its work and returns a Response

WHY IT EXISTS:
- The view is where your business logic lives
- It's the bridge between the URL (what the client asked for) and the data (what the DB has)

HOW IT WORKS (function-based view with DRF):
```
Client sends HTTP request
    ↓
urls.py matches the URL → calls the view function
    ↓
@api_view decorator checks the HTTP method is allowed
    ↓
View fetches data, runs logic, uses a serializer
    ↓
Returns a DRF Response (serialized data + status code)
    ↓
Client receives JSON
```

KEY INSIGHT:
The URL says *what resource*. The HTTP method says *what action*.
One URL can handle multiple actions (GET, POST, PATCH) — the view decides what to do based on `request.method`.

---

### @api_view Decorator

```python
@api_view(['GET', 'POST'])
def my_view(request):
    ...
```

- Wraps a plain function in DRF's request/response handling
- Whitelist of allowed methods — returns `405 Method Not Allowed` for anything else
- Gives you `request.data` (parsed request body) instead of `request.body`
- Gives you DRF's `Response` instead of Django's `JsonResponse`

Without `@api_view`, you'd have to parse JSON manually, handle content negotiation yourself, and lose the browsable API.

---

### The Request Object

DRF's `request` wraps Django's `HttpRequest` and adds:

| Attribute | What it is |
|---|---|
| `request.data` | Parsed request body (JSON, form data — works for POST, PUT, PATCH) |
| `request.query_params` | URL query string parameters (e.g. `?status=CHK`) |
| `request.method` | The HTTP method as a string (`'GET'`, `'POST'`, etc.) |
| `request.user` | The authenticated user (or AnonymousUser) |

---

### The Response Object

```python
return Response(data, status=status.HTTP_200_OK)
```

- `data`: anything serializable (dict, list, string, None)
- `status`: HTTP status code — use DRF's constants (`status.HTTP_201_CREATED`) not raw integers
- DRF handles content negotiation — if the client wants JSON, it gets JSON

Common status codes:
| Code | Constant | When to use |
|---|---|---|
| 200 | `HTTP_200_OK` | Successful GET or PATCH |
| 201 | `HTTP_201_CREATED` | Successful POST (resource created) |
| 204 | `HTTP_204_NO_CONTENT` | Successful DELETE (nothing to return) |
| 400 | `HTTP_400_BAD_REQUEST` | Validation failed |
| 404 | `HTTP_404_NOT_FOUND` | Resource not found |

---

### The Standard CRUD Pattern

Every view follows the same skeleton:

**GET (read one):**
```python
@api_view(['GET'])
def registrant_detail(request, registrant_id):
    registrant = Registrant.objects.get(pk=registrant_id)
    serializer = RegistrantSerializer(registrant)
    return Response(serializer.data)
```

**POST (create):**
```python
@api_view(['POST'])
def create_registrant(request):
    serializer = RegistrantSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
```

**PATCH (partial update):**
```python
@api_view(['PATCH'])
def update_status(request, registrant_id):
    registrant = Registrant.objects.get(pk=registrant_id)
    serializer = RegistrantSerializer(registrant, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
```

Notice the pattern for PATCH: you pass the **instance** as the first argument. This tells the serializer "update this existing object" rather than creating a new one. `partial=True` means fields not included in the request body are left unchanged.

---

### PATCH vs PUT

| | PUT | PATCH |
|---|---|---|
| Sends | All fields | Only the fields that change |
| Missing fields | Reset to default/null | Left unchanged |
| Use when | Replacing a whole resource | Updating one or two fields |

In practice, PATCH is almost always what you want for update endpoints.

---

### URL Parameters

URL parameters are passed directly as function arguments:

```python
# urls.py
path('registrants/<int:registrant_id>/status/', views.update_status)

# views.py
def update_status(request, registrant_id):  # registrant_id comes from the URL
```

The name in `<int:registrant_id>` must match the parameter name in the function signature exactly.

---

## Data Migrations

Data Migrations
===============

CONCEPT: What Is It?
--------------------
A data migration is a Django migration that doesn't just change the *structure*
of the database (schema) — it also transforms the *data inside it*.

Django has two types of migrations:
- **Schema migrations** — add/remove/alter columns and tables (auto-generated)
- **Data migrations** — run Python code to manipulate data (written by you)

WHY IT EXISTS:
- Sometimes you need to change how data is stored, not just its structure
- Simply altering a column type can destroy existing data
- Data migrations let you transform data safely before or after schema changes

HOW IT WORKS (safe approach for changing a CharField to a ForeignKey):
- Step 1: Add the new ForeignKey column as NULLABLE (existing rows unaffected)
- Step 2: Write a data migration — loop through existing rows, create the
          related objects, and populate the new column
- Step 3: Make the column non-nullable (now all rows have valid FK values)
- Step 4: Drop the old CharField

Each step is a separate migration file. The database is never in a broken state.

KEY INSIGHT:
Never try to change a column's type and migrate existing data in one step.
Always separate "add the new structure" from "move the data" from "remove the old structure".

MAIN USE CASES:
1. Changing a CharField to a ForeignKey (extracting a lookup table)
2. Splitting one column into two
3. Populating a new column based on logic from other columns
4. Backfilling data after adding a new required field

---

### The Multi-Step Pattern (CharField → ForeignKey)

**The wrong way (one step):**
```
CharField("Google") → ForeignKey(company_id=1)
```
Django tries to cast "Google" to an integer. Fails immediately.

**The right way (three steps):**

#### Step 1 — Add nullable ForeignKey (schema migration)
In `models.py`, add the new field alongside the old one:
```python
company = models.CharField(max_length=255)           # old — keep for now
company_fk = models.ForeignKey(                      # new — nullable
    Company,
    on_delete=models.PROTECT,
    null=True,
    blank=True
)
```
Run `makemigrations`. Existing rows get `company_fk = NULL`. Nothing breaks.

#### Step 2 — Data migration (populate the new column)
Create an empty migration:
```bash
python manage.py makemigrations --empty registrants --name populate_company_fk
```

Then write the `RunPython` function:
```python
from django.db import migrations

def populate_company_fk(apps, schema_editor):
    Registrant = apps.get_model('registrants', 'Registrant')
    Company = apps.get_model('registrants', 'Company')

    for registrant in Registrant.objects.all():
        company, _ = Company.objects.get_or_create(name=registrant.company)
        registrant.company_fk = company
        registrant.save()

def reverse_populate(apps, schema_editor):
    Registrant = apps.get_model('registrants', 'Registrant')
    for registrant in Registrant.objects.all():
        if registrant.company_fk:
            registrant.company = registrant.company_fk.name
            registrant.save()

class Migration(migrations.Migration):
    dependencies = [('registrants', '0004_...')]

    operations = [
        migrations.RunPython(populate_company_fk, reverse_populate),
    ]
```

**Note:** Inside data migrations, always use `apps.get_model()` — never import
models directly. This gives you the model as it was at *that point in history*,
not its current state. This prevents subtle bugs when the model changes later.

#### Step 3 — Remove old field, make new one non-nullable (schema migration)
In `models.py`:
```python
company = models.ForeignKey(Company, on_delete=models.PROTECT)  # renamed, non-nullable
```
Remove the old `company` CharField. Run `makemigrations`. Django now makes
`company_fk` non-nullable since all rows have been populated.

---

### Interview Answer Template

*"We needed to extract a CharField into a proper lookup table with a ForeignKey.
Rather than do it in one migration — which would fail trying to cast strings to
integers — we split it into three steps: first add the nullable ForeignKey
column, then write a data migration using RunPython to create the Company records
and backfill the new column, then drop the old column and make the FK non-nullable.
The database was never in a broken state, and the migration was fully reversible."*
