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
- Venv created, CLAUDE.md and course files in place
- Model plan written in notes.txt
- Tom is scaffolding the Django project, app, and models now

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
