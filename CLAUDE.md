# Gold Coast Move OS — Claude Code Project Guide

## Working Style

**This rule applies to Claude Desktop only.** In Claude Code CLI sessions, Claude edits files directly as normal — no instruct-only mode needed.

**Claude Desktop: Claude instructs, Ronnie implements.** Claude must never directly edit code files. Instead, provide clear instructions: which file to open, what to change, and the exact replacement text. Ronnie makes all edits himself.

---

## What This Project Is

Gold Coast Move OS is an AI-powered **Family Decision Intelligence Platform**. It helps families relocate by acting as a trusted advisor — not a property portal. It evaluates properties, suburbs, and schools through the lens of family life outcomes.

**The one question the platform always answers**: "Will this family likely have a better life here in five years?"

This is NOT a property search engine. It optimises for:
1. Community (25%)
2. Lifestyle (20%)
3. School ecosystem (20%)
4. Property quality (20%)
5. Financial outcome (15%)

---

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | Next.js 14 (App Router), TypeScript, Tailwind CSS, shadcn/ui |
| Backend | FastAPI (Python 3.11+) |
| Database | PostgreSQL 15 |
| ORM | SQLAlchemy 2.x async + Alembic migrations |
| Auth | Clerk (multi-user family accounts) |
| AI | OpenAI GPT-4o (scoring + narratives), GPT-4o-mini (qualitative enrichment) |
| Property scraping | Apify (REA + Domain actors — structured JSON, no HTML parsing) |
| Cache | Redis |
| Email | Resend |
| Maps | Google Maps Distance Matrix API |
| Frontend hosting | Vercel |
| Backend hosting | Railway |
| Error tracking | Sentry |
| Analytics | PostHog |

---

## Architecture Documents (Read These First)

All implementation specifications are in the `/docs` folder:

| File | Read When |
|---|---|
| `docs/GC-Move-OS-Build-Pack.md` | **Start here.** Task breakdown, implementation order, code patterns, rules. |
| `docs/GC-Move-OS-PRD.md` | Deciding what a feature should do, acceptance criteria, user stories |
| `docs/GC-Move-OS-UX-Spec.md` | Implementing any screen — layout, components, states, interactions |
| `docs/GC-Move-OS-Technical-Architecture.md` | API contracts, folder structure, auth flow, infrastructure |
| `docs/GC-Move-OS-AI-Architecture.md` | Any AI prompt, function calling schema, cost estimates |
| `docs/GC-Move-OS-Data-Architecture.md` | External data sources, pipelines, caching strategy |
| `docs/GC-Move-OS-Database-Design.md` | PostgreSQL schema, indexes, seed data SQL |

**Always read the relevant spec document before implementing a feature.**

---

## Key Design Decisions (Already Made — Do Not Revisit)

1. **Property data via Apify** — User pastes a realestate.com.au or domain.com.au URL. Apify scrapes it and returns structured JSON. OpenAI is NOT used for field extraction — only for qualitative scoring (indoor-outdoor flow, modernity, design quality) from listing description text.

2. **Multi-user family accounts** — A family has one shared record. Multiple Clerk accounts can be linked to it via the `family_users` table. Primary user invites others by email. All linked users see the same family data, with individual preference profiles tracked separately.

3. **Personas are onboarding-driven** — No hardcoded "Ronnie" or "Susie" in the code. Every family member is a data record created during onboarding. Per-member AI commentary uses the actual names from the database.

4. **Budget lives in Family Inputs** — An editable settings section (not one-time onboarding). Budget, move timeline, non-negotiables, preferences, and scoring weights are all editable at any time. Financial Score is disabled (null) until budget is set.

5. **Monorepo structure** — `apps/web` (Next.js) and `apps/api` (FastAPI) in the same repo. See Build Pack Section 3 for the complete folder structure.

6. **Scoring is modular** — Each scoring dimension (Community, Lifestyle, School, Property, Financial, Risk) is a separate service. The Family Fit Service combines them. See Technical Architecture for the service list.

---

## Critical Implementation Rules

Follow these in every file you write:

1. **Every DB query must filter by `family_id`** — data isolation is the primary security model
2. **Soft deletes only** — set `deleted_at = NOW()`, never `DELETE` records
3. **All AI calls must have a timeout and fallback** — never let an OpenAI failure crash the evaluation
4. **Confidence scores reflect data completeness** — missing fields reduce confidence, not the score itself
5. **Critical risks override all scores** — a property with `has_critical_risk = True` can never be "Prioritise Immediately"
6. **Prefer boring infrastructure** — no microservices, no event streaming, no complexity that isn't earned
7. **TypeScript types must mirror Pydantic schemas exactly** — keep them in sync

---

## Repository Structure

```
gc-move-os/
├── apps/
│   ├── web/          # Next.js frontend (Vercel)
│   └── api/          # FastAPI backend (Railway)
├── docs/             # All architecture documents (read-only reference)
├── CLAUDE.md         # This file
├── .env.example      # Template for environment variables
└── README.md
```

---

## Where to Start

Read `docs/GC-Move-OS-Build-Pack.md` Section 5 (Implementation Phases) and Section 6 (Detailed Task Breakdown).

Build in this order:
1. Phase 0 — Foundation (monorepo, Next.js, FastAPI, Clerk auth, DB connection)
2. Phase 1 — Data layer (SQLAlchemy models, Alembic migrations, seed data)
3. Phase 2 — Property ingestion (Apify integration, URL submission flow)
4. Phase 3 — Scoring engine (all 6 scoring services + orchestrator)
5. Phase 4 — Frontend core (dashboard, property report, shortlist)
6. Phase 5 — AI Advisor (chat interface with family memory)
7. Phase 6 — Intelligence features (suburb, school, preference profile)
8. Phase 7 — Polish (notifications, inspection tracker, monitoring)

**Do not skip ahead.** Each phase depends on the previous.

---

## Before Writing Any Code

Confirm these are available:
- [ ] Clerk account created, API keys in `.env`
- [ ] OpenAI API key in `.env`
- [ ] Apify account created, API token in `.env`, actor IDs confirmed for REA + Domain
- [ ] Google Maps API key with Distance Matrix API enabled
- [ ] PostgreSQL running locally (Docker or Homebrew)
- [ ] Redis running locally (Docker or Homebrew)

---

## Definition of Done

A feature is complete when:
- Backend endpoint(s) return correct data
- Frontend screen(s) match the UX Spec
- `tsc --noEmit` passes (no TypeScript errors)
- No ESLint errors
- Works end-to-end locally
- Key PostHog event fires when the feature is used

---

## Build Status

**v1.1.0 — Post-launch fixes and product improvements (2026-06-23)**

| Phase | Status | Notes |
|---|---|---|
| Phase 0 — Foundation | ✅ Complete | Next.js 14, FastAPI, Clerk auth, invite flow, monorepo |
| Phase 1 — Data layer | ✅ Complete | 34 SQLAlchemy models, 7 Alembic migrations (001–007), seed data (16 suburbs, 5 schools) |
| Phase 2 — Property ingestion | ✅ Complete | Apify scraper (REA + Domain), GPT-4o-mini qualitative enrichment, background ingestion orchestrator, migration 008, data_quality_score + extraction_confidence |
| Phase 3 — Scoring engine | ✅ Complete | travel_time, non_negotiables, community/lifestyle/school/property/risk scoring, family_fit, recommendation_service (GPT-4o), evaluation_orchestrator, GET /api/evaluations/{property_id}, migration 009 |
| Phase 4 — Frontend core | ✅ Complete | ScoreRing/FamilyFitScore/CategoryScoreRow/RecommendationBadge/PropertyCard components; typed API layer (families/properties/evaluations/dashboard); onboarding wizard (5-step); dashboard; property submission + polling; evaluation report; property list; shortlist |
| Phase 5 — AI Advisor | ✅ Complete | POST /api/advisor/chat + GET /api/advisor/history; family context injection; GPT-4o with 30s timeout + fallback; full chat UI with thread history, thinking indicator, property context banner, suggested prompts |
| Phase 6 — Intelligence features | ✅ Complete | Suburb list + detail, school comparison, preference profile, decision journal — backend routers + frontend pages |
| Phase 7 — Polish | ✅ Complete | Inspection tracker (CRUD), dashboard populated (top recs + upcoming inspections), settings page (name/invite/weights/danger zone), PostHog tracking (6 events), ErrorBoundary, active nav state, route loading spinner |

## Post-Launch Fixes (v1.1.0 — 2026-06-23)

| Fix | Files Changed |
|---|---|
| `isLoaded` guard added to all 10 page `useEffect` hooks (pages were calling `getToken()` before Clerk was ready) | All pages under `apps/web/app/app/` + `apps/web/app/app/properties/page.tsx` |
| Pool detection false negative — properties with pools in description but not structured features were failing non-negotiables | `apps/api/app/services/non_negotiables.py`, `apps/api/app/services/apify_scraper.py` |
| Dark mode default with light/dark toggle in sidebar | `apps/web/components/ThemeProvider.tsx` (new), `apps/web/app/layout.tsx`, `apps/web/app/app/layout.tsx` |
| Dashboard reduced from 2 API calls to 1 — `family_display_name` added to dashboard response | `apps/api/app/schemas/dashboard.py`, `apps/api/app/routers/dashboard.py`, `apps/web/app/app/dashboard/page.tsx`, `apps/web/lib/types/index.ts` |
| Dashboard backend: 4 sequential COUNT queries merged into 1 SQL query | `apps/api/app/routers/dashboard.py` |
| API connection pool pre-warm on startup — eliminates cold-start latency on first request | `apps/api/app/main.py` (lifespan handler) |
| Request timing middleware — logs `METHOD /path → status Xms` for every request | `apps/api/app/main.py` |
| Invite email: RESEND_API_KEY missing now logs a warning instead of silently doing nothing; `from` address changed to `onboarding@resend.dev` (no domain verification needed) | `apps/api/app/routers/families.py` |
| `FEATURES.md` created — persistent feature backlog with P1–P5 priorities | `FEATURES.md` (new) |

## Known Issues

- **Next.js hot-reload chunk 404s** — Occasionally JS chunks 404 after hot reload. Fix: restart the Next.js dev server (`npm run dev`).
- **Slow dashboard/properties in dev** — Root cause: `DATABASE_URL` points to remote Railway PostgreSQL. Every query pays network latency (~500–800ms/round trip). Fix for dev: run a local PostgreSQL via Docker and point `DATABASE_URL` to localhost. Railway DB stays as production DB. See docker command below.

```bash
# Local dev DB (fast)
docker run -d --name gcmove-db \
  -e POSTGRES_USER=gcmove -e POSTGRES_PASSWORD=gcmove -e POSTGRES_DB=gcmove \
  -p 5432:5432 postgres:15

# Then in apps/api/.env:
DATABASE_URL=postgresql+asyncpg://gcmove:gcmove@localhost:5432/gcmove

# Run migrations
cd apps/api && alembic upgrade head
```

---

## New Machine Setup

Clone the repo, then run these steps in order:

```bash
# 1. Frontend deps
cd apps/web && npm install

# 2. Backend deps
cd apps/api && pip install -r requirements.txt

# 3. Local dev DB (avoids Railway latency in dev)
docker run -d --name gcmove-db \
  -e POSTGRES_USER=gcmove -e POSTGRES_PASSWORD=gcmove -e POSTGRES_DB=gcmove \
  -p 5432:5432 postgres:15

# 4. Copy env files and fill in values (see Environment Variables section below)
cp apps/api/.env.example apps/api/.env
cp apps/web/.env.example apps/web/.env.local

# 5. Run all migrations
cd apps/api && alembic upgrade head

# 6. Start backend (from apps/api)
uvicorn app.main:app --reload --port 8000

# 7. Start frontend (from apps/web, new terminal)
npm run dev
```

The app runs at http://localhost:3000. The API runs at http://localhost:8000.

**Required env values to fill in on a new machine:**
- `OPENAI_API_KEY` — OpenAI console
- `APIFY_API_TOKEN` — Apify console
- `CLERK_SECRET_KEY` + `NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY` — Clerk dashboard
- `DATABASE_URL` — use `postgresql+asyncpg://gcmove:gcmove@localhost:5432/gcmove` for local dev
- `GOOGLE_MAPS_API_KEY` — Google Cloud console (Distance Matrix API must be enabled)
- `RESEND_API_KEY` — Resend console (optional — invite emails disabled without it)

---

## Environment Variables

- `apps/api/.env` — OpenAI ✅, Apify ✅, Clerk secret key ✅, DATABASE_URL → Railway PostgreSQL. `RESEND_API_KEY` is empty — add to enable invite emails. `CLERK_PUBLISHABLE_KEY` missing from api env.
- `apps/web/.env.local` — Clerk keys ✅. PostHog + Sentry empty (not needed yet).

Confirmed Apify actor IDs:
- REA: `memo23/realestate-au-listings`
- Domain: `fatihtahta/domain-com-au-scraper`

Next feature backlog is tracked in `FEATURES.md`.

---

## Scheduled Jobs (Railway Cron)

Auto-discovery and the Daily Brief email are plain Python modules under `apps/api/app/jobs/`, runnable identically by a developer and by Railway Cron — no in-process scheduler or task queue. Each needs its own Railway Cron Job service (a service pointed at this repo/Dockerfile with a custom start command and a cron schedule), created manually in the Railway dashboard — no `railway.json`/`railway.toml` exists yet to declare these as code, and no `railway` CLI is authenticated on any machine that's touched this repo so far.

| Job | Command | Suggested schedule |
|---|---|---|
| Auto-discovery | `python -m app.jobs.discovery_job` | Every 6 hours |
| Daily Brief email | `python -m app.jobs.daily_brief_job` | Hourly (`0 * * * *`) — the job itself gates on each family's `digest_time`, so hourly is correct, not wasteful |

Both accept `--family-id=<uuid>` and `--dry-run` for local testing without affecting real data/sends; the Daily Brief job also accepts `--force` to bypass its digest-time/idempotency gate. Run them from `apps/api` with the local venv: `.venv/bin/python -m app.jobs.discovery_job --dry-run`.

---

## Open Questions (Resolve Before Building Affected Feature)

| # | Question | Blocks |
|---|---|---|
| OQ-001 | Family budget — entered in Family Inputs during onboarding. Make mandatory with opt-out. | Financial Score |
| OQ-002 | ✅ RESOLVED — REA: memo23/realestate-au-listings / Domain: fatihtahta/domain-com-au-scraper | Property ingestion |
| OQ-005 | Google Maps API key with billing enabled? | Travel time scoring |
| OQ-007 | ABS 2021 Census data source — CSV download or API? Who loads it? | Community Score |
