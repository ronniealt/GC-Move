# Gold Coast Move OS — Claude Code Project Guide

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

## Open Questions (Resolve Before Building Affected Feature)

| # | Question | Blocks |
|---|---|---|
| OQ-001 | Family budget — entered in Family Inputs during onboarding. Make mandatory with opt-out. | Financial Score |
| OQ-002 | Confirm Apify actor IDs for REA + Domain. Test against 5 real Gold Coast URLs first. | Property ingestion |
| OQ-005 | Google Maps API key with billing enabled? | Travel time scoring |
| OQ-007 | ABS 2021 Census data source — CSV download or API? Who loads it? | Community Score |
