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
- Superuser created
- All three models complete and migrated: Event, Registrant, StatusChange
- Models registered and visible in Django admin
- Drafted LinkedIn message to CrowdComms principal about "registrant-first" approach
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
