# Session Log — CrowdComms Registration Dashboard

## Learning Approach
This is an educational project. Tom writes the code himself. Claude acts as a university lecturer — the "Mosh Next to Me" model:
1. Textbook explanations (what/why) → added to `DJANGO_DRF_COURSE.md`
2. Strategic doc navigation (filter the noise, point to the right sections)
3. Tom implements (the struggle is where learning happens)
4. Debrief and deeper understanding

Tom should be challenged. Don't give solutions. Explain the "why" and let Tom do the work.

## Prior Knowledge (from TaxConductor project)
Before this project, Tom built a Django tax calculator (`/Users/tomfyfe/codes/TaxConductor/`). Through that he learned:
- Django project/app structure, custom User model (AbstractUser, email-based auth)
- Migrations, admin setup, superuser creation
- Docker + docker-compose for Postgres
- Environment variables (.env)
- Django models: ForeignKey, on_delete (CASCADE vs PROTECT), DecimalField, CharField, Meta classes
- Plain Django views (function-based, returning JsonResponse)
- QuerySets: .all(), .filter(), .values(), .get() and their differences
- REST API principles, HTTP methods, content negotiation
- Installed DRF but hasn't created a serializer yet (understands the theory)

Full TaxConductor history: `/Users/tomfyfe/codes/TaxConductor/SESSION_LOG.md`
DRF reference notes so far: `/Users/tomfyfe/codes/TaxConductor/DJANGO_DRF_COURSE.md`

## Project Purpose
Building a registration dashboard inspired by CrowdComms' actual product (their Jan 2026 release). This gives Tom something specific and technical to discuss with the CrowdComms principal who interviewed him and is watching his LinkedIn.

## Target Role: Junior API Developer — CrowdComms (Remote, UK)
Salary: Up to £40,000

**Tech Stack:** Python, Django, DRF, FastAPI, Postgres, Redis, AWS (ECS, S3, CloudFront), Docker, Git, CI/CD

**Nice to Have:** FastAPI, Redis/caching, Celery/AMQP, Websockets

## Testing
Write unit tests as features are built using **pytest-django**. Tom has pytest experience.

## LinkedIn
Tom posts updates to LinkedIn documenting the learning journey. The CrowdComms principal is actively engaging with these posts.

## Current Phase
Phase 1: Project Setup & Core Models

## Current Status
- Django project scaffolded (`registrant_dashboard`)
- App created: `registrants`
- Docker + Postgres running (with named volume for data persistence)
- django-environ set up for .env
- DRF installed and added to INSTALLED_APPS
- pytest + pytest-django installed, pytest.ini configured
- Superuser created
- All three models complete and migrated: Event, Registrant, StatusChange
- Models registered and visible in Django admin
- EventSerializer and RegistrantSerializer built (ModelSerializer)
- event_list (GET) and create_registrant (POST) endpoints working
- Full DRF views: @api_view + Response (no longer hybrid)
- First passing test: test_create_registrant (201 status)
- Decided: StatusChange auto-creation on new registrant will live in the API layer (serializers)

## Session Notes

### Session 1 — 2026-02-15
**Topic:** Project kickoff & model design discussion

**What happened:**
- Reviewed the project purpose: building a registrant dashboard inspired by CrowdComms' Jan 2026 release
- Discussed CrowdComms' LinkedIn post about their new registration flow — they highlight a "registrant-first" approach, powerful filtering by status, and status history for admin visibility
- Discussed what "registrant-first" means: the registrant/registration is the central entity, not the event. The dashboard revolves around registrants, not events
- Discussed whether a person could register multiple times — concluded each registration is its own record (modelling a *registration*, not a *person*). Name and email are just attributes of that registration
- Discussed whether Event needs open/close times — decided event times (venue doors) are separate from check-in timestamps (tracked by StatusChange). Keeping Event simple for now: name, date, capacity
- Model plan confirmed:
  - **Event** — name, date, capacity
  - **Registrant** — name, email, company, event (FK), guest type (choices), current status (choices)
  - **StatusChange** — registrant (FK), status, timestamp

**Decisions made:**
- Registrant-first design: API and dashboard will centre on registrants
- Each registration stands alone — same person, different companies = separate records
- Keep Event model simple — no open/close times needed for a registrant dashboard
- StatusChange model gives audit trail of status transitions (aligns with CrowdComms' "status history view for admin visibility")

**What's next:**
- Tom scaffolds the Django project and app
- Writes the models in code
- Runs migrations
- Then we begin Phase 1 proper: **Creating Serializers** (first new concept)

### Session 2 — 2026-02-18
**Topic:** Project setup, Docker, models, LinkedIn outreach

**What happened:**
- Set up Django project (`registrant_dashboard`) and `registrants` app
- Configured docker-compose.yml for Postgres container (referenced TaxConductor setup)
- Troubleshot `.env` loading — learned how `BASE_DIR` resolves via `os.path.dirname()` chains
- Configured django-environ; discussed benefit over python-dotenv (type casting, defaults, Django-specific helpers)
- Decided on `registrants` as the app name (discussed conventions — short, simple, plural)
- Event model written and migrated to DB
- Created superuser to verify models in admin
- Registrant model started — still needs FK to Event, choices for guest_type and status
- StatusChange model still TODO
- Discussed `DateField` vs `DateTimeField` for Event.date — decided DateField since we don't need event open/close times
- Drafted and refined LinkedIn message to CrowdComms principal asking about "registrant-first" meaning
- Discussed how to present own thinking without overstating confidence

**Decisions made:**
- Single app (`registrants`) for all three models — they're tightly coupled
- Using django-environ for env config
- DateField for Event.date

**What's next:**
- Finish Registrant model (FK, choices fields)
- Build StatusChange model
- Migrate and verify in admin
- Then: serializers (first new concept)

### Session 2 (continued) — 2026-02-19
**Topic:** Completing models, Docker volumes, StatusChange design

**What happened:**
- Completed Registrant model: added ForeignKey to Event (PROTECT), choices for guest_type and current_status
- Learned Django choices pattern: constants + dictionary, database value vs display value, single source of truth
- Built StatusChange model: FK to Registrant (CASCADE), status field referencing Registrant's choices, DateTimeField with auto_now_add=True
- Debugged several issues:
  - Can't use instance attributes as field defaults (class-level vs instance-level)
  - `status_choices.REGISTERED` doesn't work on a dict — use `Registrant.REGISTERED` directly
  - `timezone.now()` with parentheses evaluates once at class load, not per-record — switched to auto_now_add=True
- Added Docker named volume (`db-data`) for Postgres data persistence — data was being lost between container restarts
- Ran migrations successfully, verified all models in Django admin
- Discussed where StatusChange auto-creation logic should live (model layer via signals vs API layer via serializers)

**Concepts learned:**
- Django choices pattern (constants + dict, max_length must accommodate the DB values)
- Sharing choices between models via class attribute references (`Registrant.REGISTRANT_STATUS_CHOICES`)
- `auto_now_add=True` vs `default=timezone.now` (callable without parentheses)
- Docker named volumes for data persistence
- on_delete strategies: PROTECT (safety net for Event), CASCADE (history dies with registrant)

**Decisions made:**
- StatusChange auto-creation will be handled in the API layer (serializers), not model signals — keeps it explicit and visible
- on_delete: Event→Registrant uses PROTECT, Registrant→StatusChange uses CASCADE

**What's next:**
- Begin Phase 1 proper: Creating Serializers (first new DRF concept)

### Session 3 — 2026-02-19
**Topic:** First serializer, first endpoint, LinkedIn posts

**What happened:**
- Installed DRF, added to INSTALLED_APPS
- Created `serializers.py` in registrants app (convention — not auto-generated by Django)
- Built EventSerializer using ModelSerializer — Meta class with model and fields
- Discussed doc navigation frustrations: DRF docs assume conventions (where to put files, imports), don't spell out the basics for newcomers
- Created `event_list` view: function-based, uses EventSerializer with `many=True`, returns JsonResponse
- Debugged `many=False` vs `many=True`: `.all()` returns a QuerySet (collection), not a single object — serializer needs `many=True` for collections
- Discussed design: dashboard could handle many events, UX selects current one — so list endpoint makes sense
- Discussed current setup is a hybrid: DRF serializer + plain Django view/response. Next step is full DRF views (`@api_view`, `Response`)
- Cleaned up unused imports (HttpResponse, JSONParser)
- Renamed view from `get_event` to `event_list` for clarity
- Two LinkedIn posts: one about models/choices, one about serializers/first endpoint

**Concepts learned:**
- ModelSerializer pattern: class inheriting from serializers.ModelSerializer, Meta class with model + fields
- `many=True` vs `many=False`: tells serializer whether to expect a collection or single object
- `.all()` always returns a QuerySet even if only one object exists
- `serializers.py` is a convention, not auto-generated — you create it yourself
- DRF docs have a tutorial section (tutorial/1-serialization/) that's more beginner-friendly than the API reference

**Decisions made:**
- Start with function-based views to see what the serializer does (compare to TaxConductor's manual approach)
- Event list endpoint returns all events (many=True), not just one
- Explicit field lists in serializers (better than `__all__` for clarity)

**What's next:**
- Switch to full DRF views: `@api_view` decorator and `Response` instead of `@csrf_exempt` and `JsonResponse`
- Build Registrant and StatusChange serializers
- Eventually: class-based views, ViewSets, routers

### Session 4 — 2026-02-20
**Topic:** DRF views, RegistrantSerializer, POST endpoint, testing

**What happened:**
- Upgraded event_list view from plain Django (@csrf_exempt + JsonResponse) to full DRF (@api_view + Response)
- Removed unused try/except DoesNotExist — .all() never raises it
- Built RegistrantSerializer (ModelSerializer)
- Built create_registrant POST endpoint
- Discussed URL routing: URL routes to view, @api_view decorator handles method filtering (not the URL)
- Discussed DRY principle: one URL per resource, HTTP method determines action
- Discussed views.py split: one file is fine at this scale, split when it grows
- Installed pytest-django, configured pytest.ini with DJANGO_SETTINGS_MODULE
- Wrote first test: test_create_registrant — creates Event, POSTs registrant, asserts 201
- @pytest.mark.django_db decorator required for any test that touches the ORM

**Concepts learned:**
- @api_view(['POST']) — method whitelist, returns 405 for anything else
- DRF Response vs JsonResponse — Response handles content negotiation, works with DRF renderer
- @pytest.mark.django_db — grants database access for individual tests
- APIClient — DRF test client for making requests to endpoints
- Event.objects.create() — keyword arguments, not dict syntax
- response.status_code — not response.status
- Test structure: setup (create event) → action (POST) → assertion (status code)

**Decisions made:**
- One views.py for now — split when file grows
- Tests live in registrants/tests.py

**What's next:**
- Implement StatusChange auto-creation in create_registrant view
- Write test to verify StatusChange is created alongside new Registrant
- Eventually: class-based views, ViewSets, routers

### Session 5 — 2026-02-22
**Topic:** Dashboard design, Company model, data migrations, VSCode theme

**What happened:**
- Discussed what the dashboard needs to show: count per status (registered, checked-in, entered, exited, cancelled), total attendees, count per company
- Decided `company` should be a separate `Company` model (ForeignKey) rather than a free-text CharField — prevents "Google" / "google" / "Google Inc" ambiguity
- Company model added with just `name` field; Registrant.company changed from CharField to ForeignKey
- Hit a migration error: existing row had `company="testcomp1"` — Django tried to cast the string to bigint (FK integer) and failed
- Discussed the *professional* multi-step migration pattern for this scenario (see DJANGO_DRF_COURSE.md)
- Textbook entry written in DJANGO_DRF_COURSE.md: Data Migrations — the full three-step pattern with code and interview answer template
- VSCode Semantic Darcula theme customised extensively: unified background colour (#242424), muted sidebar text (#7D8B99), soft editor text (#C5CDD6), orange badges (#CC8242), operator colours to match keywords (#CC8242), True/False/None in amber (#FFC66D), f-string prefix purple (#9E7BB0)

**Strategic thinking:**
- Tom's priority: get the MVP up across the full stack (Django/DRF → FastAPI → Redis → Celery) before the CrowdComms interview (next month)
- Plan: finish DRF MVP with function-based views, do one refactor session to class-based/generic views, then move on to FastAPI
- Tom can talk about the multi-step migration pattern in the interview — real-world scenario, professional answer

**Concepts learned:**
- Why ForeignKey > CharField for lookup data (data consistency, query reliability)
- Data migration error: Django can't cast existing string data when converting to FK
- Multi-step migration pattern: add nullable FK → data migration (RunPython) → drop old field
- `apps.get_model()` inside data migrations (never import models directly — use historical state)
- `get_or_create()` pattern for idempotent data operations
- Difference between schema migrations (auto-generated) and data migrations (hand-written RunPython)

**Decisions made:**
- Company is a proper model, not a CharField — consistent data for dashboard queries
- Will implement the multi-step migration pattern professionally (not the quick delete-and-migrate dev shortcut)
- MVP-first strategy: breadth across the stack > perfecting DRF

**What's next:**
- Implement the multi-step data migration for Company (Step 1: add nullable FK)
- Write data migration (RunPython) to populate company_fk from existing company string
- Drop old CharField, make FK non-nullable
- Continue CRUD endpoints for the dashboard
