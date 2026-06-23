# GC Move OS — Feature Backlog

Last updated: 2026-06-23

---

## In Progress

_Nothing currently in progress._

---

## Prioritised Backlog

### P1 — Property Dismiss / Archive
**Status:** Ready to build  
**Effort:** Small (~ 1–2 hours)

Allow a property to be marked "Not interested" and hidden from the dashboard and properties list without deleting it. Dismissed properties are soft-hidden and reversible.

**Backend:**
- Support `dismissed` as a valid property status in `PATCH /api/properties/{id}`
- Exclude `dismissed` properties from the dashboard `top_recommendations` query
- Exclude `dismissed` from the default `GET /api/properties` list response
- No migration needed — status is a plain string column

**Frontend:**
- Add "Not interested" dismiss button to `PropertyCard` component
- Add dismiss button to the property detail page (`/app/properties/[id]`)
- Filter dismissed from dashboard and properties list by default
- Optional: "Show dismissed" toggle on the properties list page

---

### P2 — Score Transparency ("Why this score?")
**Status:** Ready to build  
**Effort:** Medium (~ half day)

Every dimension score on the property report gets an expandable "How was this scored?" breakdown showing the actual data inputs. Eliminates the black box and builds trust in the scores.

**Backend:**
- Extend the evaluation response to include `score_breakdown` per dimension
- Community breakdown: owner-occupier rate, family density %, median weekly income, crime index
- Lifestyle breakdown: beach access minutes, Burleigh drive minutes, café count, gym count, park count
- School breakdown: nearest pinned school distance, school score
- Property breakdown: qualitative scores (modernity, indoor/outdoor flow, design quality, etc.)
- Data is already in the DB — just needs to be included in the API response

**Frontend:**
- Add expandable accordion per dimension on the property report page (`/app/properties/[id]`)
- Each panel shows the data points and how they contributed to the score
- Example: "Community 7.6 → Owner-occupiers 74%, Family households 38%, Crime index 2.1"

---

### P3 — Schools: Suburb Filter + Family Pin
**Status:** Ready to build  
**Effort:** Medium (~ half day)

Replace the hardcoded featured schools list with a dynamic, family-managed pin system. Pick target suburbs → see schools in catchment → pin the ones that matter. Pinned schools surface on property evaluations.

**Backend:**
- New `family_schools` table: `family_id`, `school_id`, `created_at`
- New Alembic migration (010)
- `POST /api/families/{id}/schools` — pin a school
- `DELETE /api/families/{id}/schools/{school_id}` — unpin
- `GET /api/schools?suburb=Burleigh+Heads` — filter schools by suburb name
- Include pinned schools + distances on property evaluation response

**Frontend:**
- Schools page: add suburb filter dropdown (populated from seeded suburb list)
- Replace hardcoded `FEATURED_ACARA_IDS_NAMES` with dynamic pinned schools from API
- Add "Pin" / "Unpin" button to `SchoolCard`
- Pinned schools section at top of Schools page (already has the UI pattern — just needs to be dynamic)
- Property report: show nearest pinned schools with drive time

---

### P4 — Performance: Single API Call + Pagination
**Status:** Ready to build  
**Effort:** Small (~ 1–2 hours)

Dashboard fires two API calls (family + dashboard data) sequentially. Properties list loads all records at once. Both cause noticeable load delays.

**Backend:**
- Extend `GET /api/dashboard` response to include `family_display_name` so the dashboard page needs only one call
- Add `limit` and `offset` query params to `GET /api/properties` (default limit 20)

**Frontend:**
- Dashboard page: remove `getMyFamily` call, pull display name from dashboard response
- Properties list page: implement pagination UI (Next / Previous or load more)

---

## Phase 2 Backlog

### P5 — Dashboard UI Redesign (AIMomentum-style)
**Status:** Parked — design pass after core features are stable  
**Effort:** Medium (~ 1 day)  
**Reference:** AIMomentum Hub (Insentra) — screenshot on file

A visual and UX refresh of the dashboard to match the polished, high-impact feel of the AIMomentum Hub.

**Key changes:**
- **Dark theme** — navy/dark background with high-contrast white typography (or add a dark mode toggle)
- **Bold personalised hero** — large uppercase "WELCOME BACK, [FAMILY NAME]" as the page centrepiece, replacing the current small greeting
- **Purpose-driven quick-action cards** — 4 cards below the hero: "Looking at a property", "Exploring suburbs", "Checking schools", "Talking to your advisor" — each linking to the relevant section
- **Move journey timeline** — visual 4–5 step progress indicator (Explore → Shortlist → Inspect → Decide → Move) showing where the family currently sits
- **Sidebar polish** — add icons to each nav item, tighten spacing, add family avatar/initials at bottom
- **Announcement banner** — surface new properties evaluated or new suburb data since last visit
- **Stronger card hierarchy** — top recommendations as hero cards, not just a horizontal scroll

**Notes:**
- The AIMomentum Hub screenshot shows the exact target aesthetic
- Tailwind dark mode (`dark:` classes) + a `dark` class on the root `<html>` is the simplest implementation path
- Could ship dark theme first as a quick win, then tackle layout in a second pass

---

### P6 — Social Media + Review Signals
**Status:** Parked — plan separately when core is solid  
**Effort:** Large (new data pipeline)

Integrate external review and sentiment data into community and lifestyle dimension scores.

**Potential sources:**
- Google Places API — suburb and local business reviews
- REA suburb review scores
- Facebook community group sentiment (scrape or manual seed)

**Notes:**
- Would meaningfully improve the accuracy of Community and Lifestyle scores
- Requires a new async data pipeline, likely a scheduled Apify or API job
- Scores would need confidence weighting to reflect data freshness

---

## Completed

| Feature | Date | Notes |
|---|---|---|
| Phase 0 — Foundation | 2025 | Next.js 14, FastAPI, Clerk auth, invite flow, monorepo |
| Phase 1 — Data layer | 2025 | 34 SQLAlchemy models, 7 Alembic migrations, seed data |
| Phase 2 — Property ingestion | 2025 | Apify scraper (REA + Domain), GPT-4o-mini enrichment |
| Phase 3 — Scoring engine | 2025 | All 6 scoring services + orchestrator |
| Phase 4 — Frontend core | 2025 | Dashboard, property report, shortlist, onboarding |
| Phase 5 — AI Advisor | 2025 | Chat interface with family memory and context |
| Phase 6 — Intelligence features | 2025 | Suburb list/detail, school comparison, preference profile |
| Phase 7 — Polish | 2025 | Inspection tracker, settings, PostHog tracking, error handling |
| Fix: isLoaded guard on all pages | 2026-06-23 | useEffect hooks now wait for Clerk auth before calling getToken() |
| Fix: Pool detection false negative | 2026-06-23 | non_negotiables.py now checks description text as fallback; apify_scraper.py widens feature field search |
