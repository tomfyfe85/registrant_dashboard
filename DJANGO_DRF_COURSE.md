# Django REST Framework Course - TaxConductor Edition
=====================================================

A textbook-style reference guide built alongside the TaxConductor project.
Each concept includes: theory, examples, and implementation options.

---

## Table of Contents
1. [Serializers](#serializers)
2. [Views & ViewSets](#views--viewsets) (Coming soon)
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

*Last updated: 2026-02-12*
