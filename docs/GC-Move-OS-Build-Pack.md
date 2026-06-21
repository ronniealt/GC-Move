# Gold Coast Move OS — Claude Code Build Pack
### Version 1.0 | Implementation Guide for Developers

---

## 0. How to Use This Document

This Build Pack is the single source of truth for implementing Gold Coast Move OS. It references the six companion documents:

- `GC-Move-OS-PRD.md` — product requirements and user stories
- `GC-Move-OS-UX-Spec.md` — screen specs, flows, and component definitions
- `GC-Move-OS-Technical-Architecture.md` — system architecture, API contracts, infrastructure
- `GC-Move-OS-AI-Architecture.md` — AI pipeline, prompts, function calling schemas
- `GC-Move-OS-Data-Architecture.md` — data sources, pipelines, caching strategy
- `GC-Move-OS-Database-Design.md` — PostgreSQL schema, indexes, seed data

Read all six documents before writing any code. This document tells you **what to build, in what order, and how to know when it is done.**

---

## 1. Project Summary

**Product**: Gold Coast Move OS — AI-powered Family Decision Intelligence Platform.

**Mission**: Help families choose a better life, not just a better house. Every recommendation must answer: *"Will this family likely have a better life here in five years?"*

**MVP Scope**: A single authenticated family (the Altit family: Ronnie, Susie, Austin, Mabel) can submit property URLs, receive AI-generated evaluations scored across Community / Lifestyle / School / Property / Financial dimensions, explore suburb intelligence, compare schools, maintain a decision journal, and consult an AI advisor that remembers their preferences.

**Not in MVP**: Multi-family support, native mobile app, PropTrack API integration, payment processing, mortgage broking, property management.

---

## 2. Technology Stack

| Layer | Technology | Version |
|---|---|---|
| Frontend | Next.js | 14 (App Router) |
| Language | TypeScript | 5.x |
| Styling | Tailwind CSS | 3.x |
| Components | shadcn/ui | latest |
| Backend | FastAPI | 0.111+ |
| Backend Language | Python | 3.11+ |
| Database | PostgreSQL | 15 |
| ORM | SQLAlchemy | 2.x async |
| Migrations | Alembic | latest |
| Auth | Clerk | latest |
| AI | OpenAI | 1.x Python SDK |
| Cache | Redis | 7.x |
| Email | Resend | latest |
| Maps | Google Maps Platform | Distance Matrix API |
| Frontend Host | Vercel | - |
| Backend Host | Railway | - |
| Error Tracking | Sentry | - |
| Analytics | PostHog | - |
| HTTP Client | httpx | async |
| HTML Parser | BeautifulSoup4 | latest |

---

## 3. Repository Structure

Use a **monorepo** with two workspaces:

```
gc-move-os/
├── apps/
│   ├── web/                        # Next.js frontend
│   │   ├── app/                    # App Router pages
│   │   │   ├── (auth)/             # Auth group (login, signup)
│   │   │   ├── (app)/              # Protected app group
│   │   │   │   ├── dashboard/
│   │   │   │   ├── properties/
│   │   │   │   ├── suburbs/
│   │   │   │   ├── schools/
│   │   │   │   ├── journal/
│   │   │   │   ├── advisor/
│   │   │   │   ├── shortlist/
│   │   │   │   ├── inspections/
│   │   │   │   ├── preferences/
│   │   │   │   └── settings/
│   │   │   ├── onboarding/         # Onboarding flow (separate from app)
│   │   │   ├── layout.tsx
│   │   │   └── page.tsx
│   │   ├── components/
│   │   │   ├── ui/                 # shadcn components (auto-generated)
│   │   │   ├── scores/             # Score display components
│   │   │   ├── properties/         # Property-specific components
│   │   │   ├── advisor/            # AI advisor chat components
│   │   │   ├── journal/
│   │   │   ├── suburbs/
│   │   │   ├── schools/
│   │   │   └── shared/             # Shared layout and nav
│   │   ├── lib/
│   │   │   ├── api/                # API client (typed fetch wrappers)
│   │   │   ├── hooks/              # Custom React hooks
│   │   │   ├── stores/             # Zustand stores
│   │   │   ├── types/              # TypeScript types (match API contracts)
│   │   │   └── utils/
│   │   ├── public/
│   │   ├── tailwind.config.ts
│   │   ├── next.config.ts
│   │   └── package.json
│   │
│   └── api/                        # FastAPI backend
│       ├── app/
│       │   ├── main.py             # App factory, CORS, middleware
│       │   ├── config.py           # Settings (pydantic-settings)
│       │   ├── database.py         # Async engine, session factory
│       │   ├── dependencies.py     # FastAPI DI (auth, db session)
│       │   ├── routers/
│       │   │   ├── families.py
│       │   │   ├── properties.py
│       │   │   ├── evaluations.py
│       │   │   ├── suburbs.py
│       │   │   ├── schools.py
│       │   │   ├── advisor.py
│       │   │   ├── journal.py
│       │   │   ├── inspections.py
│       │   │   ├── preferences.py
│       │   │   └── dashboard.py
│       │   ├── services/
│       │   │   ├── property_ingestion.py
│       │   │   ├── property_scoring.py
│       │   │   ├── community_scoring.py
│       │   │   ├── lifestyle_scoring.py
│       │   │   ├── school_scoring.py
│       │   │   ├── risk_scoring.py
│       │   │   ├── family_fit.py
│       │   │   ├── preference_learning.py
│       │   │   ├── memory_service.py
│       │   │   ├── recommendation_service.py
│       │   │   ├── explainability.py
│       │   │   ├── decision_journal.py
│       │   │   ├── travel_time.py
│       │   │   └── ai_advisor.py
│       │   ├── ai/
│       │   │   ├── client.py       # OpenAI client singleton
│       │   │   ├── prompts/        # Prompt templates as .py files
│       │   │   │   ├── property_extraction.py
│       │   │   │   ├── property_scoring.py
│       │   │   │   ├── recommendation.py
│       │   │   │   ├── advisor.py
│       │   │   │   ├── preference_inference.py
│       │   │   │   └── five_year_prediction.py
│       │   │   ├── functions/      # Function calling schemas
│       │   │   └── context.py      # Family context serialiser
│       │   ├── models/             # SQLAlchemy ORM models
│       │   ├── schemas/            # Pydantic request/response schemas
│       │   ├── cache/              # Redis cache helpers
│       │   └── utils/
│       ├── alembic/
│       │   └── versions/
│       ├── tests/
│       ├── alembic.ini
│       ├── pyproject.toml
│       └── Dockerfile
├── packages/
│   └── shared-types/               # Shared TypeScript types (optional)
├── .env.example
├── .github/
│   └── workflows/
│       ├── ci.yml
│       └── deploy.yml
└── README.md
```

---

## 4. Environment Variables

### Frontend (`apps/web/.env.local`)
```
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=
CLERK_SECRET_KEY=
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_POSTHOG_KEY=
NEXT_PUBLIC_POSTHOG_HOST=https://app.posthog.com
NEXT_PUBLIC_SENTRY_DSN=
```

### Backend (`apps/api/.env`)
```
DATABASE_URL=postgresql+asyncpg://user:pass@host:5432/gcmove
REDIS_URL=redis://localhost:6379
OPENAI_API_KEY=
OPENAI_MODEL_MAIN=gpt-4o
OPENAI_MODEL_FAST=gpt-4o-mini
CLERK_PUBLISHABLE_KEY=
CLERK_SECRET_KEY=
GOOGLE_MAPS_API_KEY=
RESEND_API_KEY=
SENTRY_DSN=
APIFY_API_TOKEN=
APIFY_REA_ACTOR_ID=           # Confirm before build — test via Apify console
APIFY_DOMAIN_ACTOR_ID=        # Confirm before build — test via Apify console
CORS_ORIGINS=http://localhost:3000,https://gcmoveos.vercel.app
LOG_LEVEL=INFO
```

---

## 5. Implementation Phases

### Phase 0 — Foundation (Week 1)
Get the project running end to end with auth working.

### Phase 1 — Core Data Layer (Week 2)
Database schema, migrations, seed data.

### Phase 2 — Property Ingestion (Week 3)
URL paste → AI extraction → property record.

### Phase 3 — Scoring Engine (Week 4–5)
All scoring services. Evaluation pipeline.

### Phase 4 — Frontend Core (Week 6–7)
Dashboard, property report, shortlist.

### Phase 5 — AI Advisor (Week 8)
Conversational interface with memory.

### Phase 6 — Intelligence Features (Week 9)
Suburb detail, school comparison, preference profile.

### Phase 7 — Polish & Launch (Week 10)
Notifications, inspection tracker, performance, monitoring.

---

## 6. Detailed Task Breakdown

### PHASE 0 — FOUNDATION

**Task 0.1 — Monorepo Setup**
- Initialise repo with the structure defined in Section 3
- Configure `pnpm` workspaces
- Add `.gitignore`, `.env.example`
- Done when: `pnpm install` runs without errors

**Task 0.2 — Next.js App Init**
- `npx create-next-app@latest apps/web --typescript --tailwind --app`
- Install shadcn/ui: `npx shadcn@latest init`
- Install Clerk: `npm install @clerk/nextjs`
- Install React Query: `npm install @tanstack/react-query`
- Install Zustand: `npm install zustand`
- Install Sentry: `npx @sentry/wizard@latest -i nextjs`
- Done when: `pnpm dev` renders default Next.js page

**Task 0.3 — FastAPI App Init**
- Create `pyproject.toml` with dependencies: `fastapi`, `uvicorn`, `sqlalchemy[asyncio]`, `asyncpg`, `alembic`, `pydantic-settings`, `openai`, `httpx`, `beautifulsoup4`, `redis`, `sentry-sdk`, `python-jose`, `httpx`
- Create `app/main.py` with CORS middleware, Sentry init, health check endpoint
- Done when: `uvicorn app.main:app --reload` starts and `GET /health` returns `{"status": "ok"}`

**Task 0.4 — Clerk Authentication (Multi-User Family Model)**

Frontend:
- Wrap root layout with `<ClerkProvider>`
- Create middleware.ts with `clerkMiddleware()` protecting `/app/*` and `/onboarding/*` routes
- Create sign-in page at `app/(auth)/sign-in/[[...sign-in]]/page.tsx`
- Create sign-up page at `app/(auth)/sign-up/[[...sign-up]]/page.tsx`
- Create invite acceptance page at `app/(auth)/invite/accept/page.tsx` — reads `?token=` param, links the newly-signed-up Clerk user to the family
- Done when: unauthenticated users are redirected to sign-in from protected routes

Backend:
- Create `app/dependencies.py` with multi-user family resolution:
  - `verify_clerk_jwt()` → verifies Clerk JWT, returns `clerk_user_id`
  - `get_current_user_and_family()` → looks up `family_users` table by `clerk_user_id`, returns `(FamilyUser, Family)` tuple
  - `get_current_family()` → convenience dependency returning just `Family`
  - `get_current_family_user()` → convenience dependency returning just `FamilyUser` (needed for per-user preference capture)
- Add invite endpoints:
  - `POST /api/families/{id}/invite` — primary user sends invite (creates `family_invites` record, sends email via Resend)
  - `GET /api/invite/validate?token=` — validate invite token, return family name + inviter name
  - `POST /api/invite/accept` — authenticated user accepts invite (creates `family_users` record, marks invite as accepted)
  - `DELETE /api/families/{id}/users/{user_id}` — primary user removes a family member
- Done when: Ronnie can invite Susie by email, Susie signs up, and both can log in and see the same family data

**Task 0.5 — Database Setup (Railway)**
- Provision PostgreSQL 15 on Railway
- Provision Redis on Railway
- Configure `alembic.ini` with async SQLAlchemy URL
- Create `alembic/env.py` for async migrations
- Done when: `alembic upgrade head` runs against Railway DB with no errors

---

### PHASE 1 — DATA LAYER

**Task 1.1 — SQLAlchemy Models**

Create ORM models in `app/models/` matching the complete schema in `GC-Move-OS-Database-Design.md`. Create one file per domain:
- `models/family.py` — Family, FamilyMember, FamilyPreference, FamilyMemory, MemoryEvent
- `models/property.py` — Property, PropertyFeature, PropertyImage, PropertyHistory
- `models/location.py` — Suburb, SuburbMetric, SuburbLifestyleAsset, School, SchoolCatchment, SchoolMetric
- `models/intelligence.py` — PropertyEvaluation, EvaluationScore, EvaluationPerMember, Recommendation, RecommendationExplanation
- `models/events.py` — PreferenceEvent, DecisionJournalEntry, DecisionJournalMemberImpact
- `models/operational.py` — Inspection, AIAdvisorThread, AIAdvisorMessage, NotificationSettings, AuditLog

**Base model** (`models/base.py`):
```python
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import Column, DateTime, func
import uuid

class Base(DeclarativeBase):
    pass

class TimestampMixin:
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    deleted_at = Column(DateTime(timezone=True), nullable=True)
```

Done when: all models import without errors and `alembic revision --autogenerate` detects all tables.

**Task 1.2 — Initial Migration**

Run `alembic revision --autogenerate -m "001_initial_schema"`. Review the generated migration. Add:
- All indexes from `GC-Move-OS-Database-Design.md` Section 3
- `gen_random_uuid()` as default for all UUID PKs
- FTS index creation (GIN on tsvector columns)

Done when: `alembic upgrade head` creates all 28 tables cleanly.

**Task 1.3 — Seed Data Migration**

Create `alembic/versions/002_seed_data.py`. Insert:
- 16 Gold Coast suburbs with tier classifications and initial scores (see `GC-Move-OS-Database-Design.md` Section 4)
- Somerset College and All Saints school records
- 10 lifestyle asset categories

Done when: `alembic upgrade head` inserts all seed records; `SELECT COUNT(*) FROM suburbs` returns 16.

**Task 1.4 — Pydantic Schemas**

Create `app/schemas/` with request/response models matching every API endpoint in `GC-Move-OS-Technical-Architecture.md` Section 4. Use Pydantic v2 with `model_config = ConfigDict(from_attributes=True)` for ORM serialisation.

Key schemas:
- `FamilyCreate`, `FamilyResponse`, `FamilyUpdate`
- `FamilyMemberCreate`, `FamilyMemberResponse`
- `PropertyIngestRequest`, `PropertyResponse`, `PropertyListResponse`
- `EvaluationResponse` (includes all scores + explanation + per-member commentary)
- `RecommendationResponse`
- `SuburbResponse`, `SchoolResponse`
- `AdvisorMessageRequest`, `AdvisorMessageResponse`
- `JournalEntryResponse`
- `PreferenceResponse`
- `DashboardResponse`

Done when: all schemas import without errors and pass Pydantic validation tests.

---

### PHASE 2 — PROPERTY INGESTION

**Task 2.1 — URL Ingestion Endpoint**

`POST /api/properties/ingest`
```python
# Request: { url: str, family_id: str }
# Response: { property_id: str, status: "processing" | "complete" | "failed" }
```

Steps:
1. Validate URL pattern (`realestate.com.au` or `domain.com.au`)
2. Create a `Property` record with `status = "ingesting"` and return `property_id` immediately
3. Dispatch background task: `BackgroundTasks.add_task(ingest_property, property_id, url, family_id)`
4. Client polls `GET /api/properties/{id}` checking status

Done when: submitting a valid REA or Domain URL returns a property_id within 200ms.

**Task 2.2 — Apify Property Scraper**

**Pre-condition**: Confirm Apify actor IDs for realestate.com.au and domain.com.au before this task begins. Test both actors against 5 real Gold Coast listing URLs manually via the Apify console. Note the exact field names returned by each actor.

Install Apify client: `pip install apify-client`

`services/property_ingestion.py`:
```python
from apify_client import ApifyClient
from app.config import settings

async def fetch_property_via_apify(url: str) -> dict:
    """
    Submit a listing URL to the appropriate Apify actor.
    Returns structured property JSON (no HTML parsing needed).
    """
    client = ApifyClient(settings.APIFY_API_TOKEN)
    actor_id = (
        settings.APIFY_REA_ACTOR_ID
        if "realestate.com.au" in url
        else settings.APIFY_DOMAIN_ACTOR_ID
    )
    run = client.actor(actor_id).call(
        run_input={"startUrls": [{"url": url}], "maxItems": 1},
        timeout_secs=60
    )
    items = list(client.dataset(run["defaultDatasetId"]).iterate_items())
    if not items:
        raise PropertyExtractionError(f"Apify returned no data for: {url}")
    return items[0]

def map_apify_to_property(raw: dict, url: str) -> ExtractedPropertyData:
    """
    Normalise Apify output to internal schema.
    Field mapping will differ between REA and Domain actors.
    """
    return ExtractedPropertyData(
        address=raw.get("address") or raw.get("displayableAddress"),
        suburb=raw.get("suburb"),
        postcode=raw.get("postcode"),
        price_display=raw.get("price") or raw.get("priceText"),
        bedrooms=raw.get("bedrooms"),
        bathrooms=raw.get("bathrooms"),
        car_spaces=raw.get("carSpaces") or raw.get("parking"),
        land_size_sqm=raw.get("landArea") or raw.get("landSize"),
        house_size_sqm=raw.get("buildingArea") or raw.get("floorArea"),
        property_type=raw.get("propertyType", "house"),
        description=raw.get("description", ""),
        features=raw.get("features", []),
        image_urls=raw.get("images", []),
        agent_name=raw.get("agentName"),
        listed_date=raw.get("listingDate"),
        source_url=url,
        raw_data=raw,  # Store original for debugging
    )
```

Add `APIFY_API_TOKEN`, `APIFY_REA_ACTOR_ID`, `APIFY_DOMAIN_ACTOR_ID` to Railway env vars.

Done when: pasting a real REA listing URL results in a populated Property record with all available structured fields — without any OpenAI extraction call.

**Task 2.3 — AI Qualitative Enrichment (OpenAI)**

Apify handles all structured fields. OpenAI is only called for **qualitative attributes** that aren't captured structurally:

`ai/prompts/property_qualitative.py`:
```python
QUALITATIVE_PROMPT = """
You are evaluating a property listing to estimate qualitative attributes not available in structured data.

LISTING DESCRIPTION:
{description}

FEATURES LIST:
{features}

Estimate the following attributes on a 0–10 scale:
- modernity: How modern does this property appear? (10 = brand new/fully renovated, 1 = very dated)
- design_quality: How architecturally distinguished? (10 = custom architect-designed, 1 = standard spec build)
- indoor_outdoor_flow: How well does the layout connect indoor/outdoor spaces? (estimate from description)
- home_office_suitability: Is there a dedicated or clearly suitable home office space? (10 = dedicated room, 5 = possible, 1 = no)
- entertaining_space: How suitable for entertaining? (pool, outdoor area, kitchen size)
- privacy: Estimated privacy from description and block characteristics

Return a JSON object with these 6 scores. If you cannot estimate a score confidently from the description alone, return null.
"""
```

Call GPT-4o-mini (cost-efficient, fast). Validate output with Pydantic. These scores feed directly into the Property Score calculation.

Done when: the qualitative scores are populated for a real listing and the Property Score calculation uses them correctly.

**Task 2.4 — Travel Time Calculation**

`services/travel_time.py`:
After property is created, call Google Maps Distance Matrix API to calculate:
- Drive time from property to Burleigh Heads (target: Burleigh Heads beach carpark at -28.0897, 153.4434)
- Drive time from property to nearest beach (calculate nearest of 5 anchor points)

Store results in `property_features` as:
- `burleigh_drive_minutes` 
- `beach_drive_minutes`

Done when: ingested properties have travel time data populated.

**Task 2.5 — Non-Negotiable Filter**

After ingestion, immediately evaluate non-negotiables:
```python
NON_NEGOTIABLES = {
    "property_type": lambda p: p.property_type == "house",
    "has_pool": lambda p: "pool" in p.features,
    "within_budget": lambda p: p.price_max is None or p.price_max <= family.budget_max,
    "burleigh_access": lambda p: p.burleigh_drive_minutes is None or p.burleigh_drive_minutes <= 20,
    "beach_access": lambda p: p.beach_drive_minutes is None or p.beach_drive_minutes <= 20,
}
```

If any non-negotiable fails, set property status to `"filtered"` with reason. Still show the property to the family but display a clear warning banner.

Done when: a known unit listing is correctly flagged as failing the `property_type` non-negotiable.

---

### PHASE 3 — SCORING ENGINE

Build each scoring service independently. Each service takes a `property_id` and `family_id`, loads the necessary data, and returns a typed score object.

**Task 3.1 — Community Scoring Service**

`services/community_scoring.py`:

Input: `suburb_id` (from property's suburb)

Load from DB:
- `suburbs.owner_occupier_rate`
- `suburbs.family_density`
- `suburbs.educational_attainment`
- `suburbs.median_income`
- `suburbs.crime_index`
- `suburbs.community_engagement`

Formula:
```python
def calculate_community_score(suburb: Suburb) -> float:
    score = (
        normalise(suburb.owner_occupier_rate, 0.5, 1.0) * 0.30 +
        normalise(suburb.family_density, 0.2, 0.6) * 0.20 +
        normalise(suburb.educational_attainment, 0.3, 0.8) * 0.15 +
        normalise(suburb.median_income, 60000, 150000) * 0.15 +
        normalise(10 - suburb.crime_index, 0, 10) * 0.15 +  # invert crime
        normalise(suburb.community_engagement, 0, 10) * 0.05
    ) * 10
    return round(min(max(score, 0), 10), 1)
```

Done when: Robina scores 7.5+, known high-crime suburbs score below 5.

**Task 3.2 — Lifestyle Scoring Service**

`services/lifestyle_scoring.py`:

Inputs: `property_id` (for travel times), `suburb_id` (for POI counts)

```python
def calculate_lifestyle_score(property: Property, suburb: Suburb) -> float:
    burleigh_score = score_travel_time(property.burleigh_drive_minutes, ideal=10, max_acceptable=20)
    beach_score = score_travel_time(property.beach_drive_minutes, ideal=5, max_acceptable=15)
    wellness_score = normalise(suburb.wellness_poi_count, 0, 20)
    cafe_score = normalise(suburb.cafe_poi_count, 0, 15)
    outdoor_score = normalise(suburb.park_poi_count, 0, 10)
    shopping_score = normalise(suburb.shopping_poi_count, 0, 10)

    return round((
        burleigh_score * 0.25 +
        beach_score * 0.20 +
        wellness_score * 0.20 +
        cafe_score * 0.15 +
        outdoor_score * 0.10 +
        shopping_score * 0.10
    ) * 10, 1)

def score_travel_time(minutes: Optional[int], ideal: int, max_acceptable: int) -> float:
    if minutes is None: return 0.5  # uncertainty penalty
    if minutes <= ideal: return 1.0
    if minutes <= max_acceptable: return 1.0 - ((minutes - ideal) / (max_acceptable - ideal)) * 0.5
    return max(0, 1.0 - ((minutes - max_acceptable) / 10) * 0.5)
```

Done when: Palm Beach properties score higher on beach access than Robina properties.

**Task 3.3 — School Scoring Service**

`services/school_scoring.py`:

Determine which schools are within 20 minutes of the property. Score the school ecosystem, not just a single school. Give bonus points for Somerset College or All Saints proximity.

```python
def calculate_school_score(property: Property, family: Family) -> tuple[float, list[str]]:
    # Find schools within 20 min drive
    nearby_schools = get_schools_near_property(property)
    if not nearby_schools:
        return 3.0, ["No quality schools within 20 minutes"]
    
    # Score each school
    school_scores = [score_individual_school(s) for s in nearby_schools]
    best_score = max(school_scores)
    
    # Bonus for preferred schools
    preferred_names = ["Somerset College", "All Saints Anglican School"]
    if any(s.name in preferred_names for s in nearby_schools):
        best_score = min(10, best_score + 0.5)
    
    return round(best_score, 1), generate_school_commentary(nearby_schools)
```

Individual school score formula (from v0.3 Project Bible):
```
wellbeing × 0.25 + parent_community × 0.20 + academic × 0.20 + commute × 0.15 + extracurricular × 0.10 + pathway × 0.10
```

Done when: Properties near Somerset College score 8+ on School Score.

**Task 3.4 — Property Scoring Service**

`services/property_scoring.py`:

This service uses AI assistance. The deterministic part scores known features; AI generates the modernity/design quality/indoor-outdoor narrative component.

Deterministic scores (from extracted features):
- `has_pool` → pool score: 10 if yes, 0 if no
- `has_home_office` → office score
- `bedrooms` → bedroom score (5br = 10, 4br = 7, <4 = 4)
- `land_size_sqm` → block utility score

AI-assisted scores (call GPT-4o-mini with listing description and images):
- Modernity estimate
- Design quality estimate
- Indoor-outdoor flow estimate
- Privacy estimate
- Entertaining space estimate

Property score formula:
```
modernity × 0.20 + design × 0.15 + indoor_outdoor × 0.15 + pool × 0.10 + office × 0.10 + entertaining × 0.10 + privacy × 0.10 + block_utility × 0.10
```

Done when: a modern coastal home with pool scores 7.5+; an older house without pool scores below 5.

**Task 3.5 — Risk Scoring Service**

`services/risk_scoring.py`:

Risk categories (from v0.3 Project Bible):
- Flood risk (query QLD flood data or suburb flood_risk field)
- Road noise (proximity to major roads — check if address is within 100m of arterial road from OSM data)
- Aircraft noise (proximity to Gold Coast Airport — flag if within 10km of runway centreline)
- Crime trends (suburb crime index trends — worsening = moderate risk)
- Future development (suburb zoning data — flag if mixed-use zoning adjacent)

Risk levels: `low` | `moderate` | `high` | `critical`

Critical risks: `["high_flood_risk", "no_pool", "attached_dwelling", "outside_budget"]`

```python
def calculate_risk_score(property, suburb) -> RiskResult:
    risks = []
    
    if suburb.flood_risk_level == "high":
        risks.append(Risk(category="flood", level="critical", description="High flood risk zone"))
    
    if property.burleigh_drive_minutes and property.burleigh_drive_minutes > 25:
        risks.append(Risk(category="access", level="moderate", description="Over 25 minutes from Burleigh"))
    
    # ... more risk checks
    
    has_critical = any(r.level == "critical" for r in risks)
    return RiskResult(risks=risks, has_critical_risk=has_critical)
```

Done when: a property in a flood zone returns `has_critical_risk = True` and blocks `PrioritiseImmediately` recommendation.

**Task 3.6 — Family Fit Service**

`services/family_fit.py`:

Combines all scores using the master formula:
```python
def calculate_family_fit(
    community: float,
    lifestyle: float,
    school: float,
    property_score: float,
    financial: float
) -> float:
    return round(
        community * 0.25 +
        lifestyle * 0.20 +
        school * 0.20 +
        property_score * 0.20 +
        financial * 0.15,
        1
    )
```

Also calculates Five-Year Fit Score using the weighting from v0.4:
```
community_belonging × 0.20 + child_friendships × 0.15 + parent_friendships × 0.15 +
lifestyle_improvement × 0.15 + school_fit × 0.15 + home_satisfaction × 0.10 +
financial_comfort × 0.05 + regret_risk × 0.05
```

Recommendation logic:
```python
def determine_recommendation(
    family_fit: float,
    confidence: float,
    has_critical_risk: bool,
    meets_non_negotiables: bool
) -> str:
    if not meets_non_negotiables or has_critical_risk:
        return "ignore"
    if family_fit >= 90 and confidence >= 0.70:
        return "prioritise_immediately"
    if family_fit >= 80 and confidence >= 0.55:
        return "inspect"
    if family_fit >= 70:
        return "monitor"
    return "ignore"
```

Done when: the family fit score correctly weights all five dimensions and recommendation levels match the rules.

**Task 3.7 — AI Recommendation Generation**

`services/recommendation_service.py`:

This is the most important AI call. It takes all scores plus family context and generates the full recommendation report. Use the complete prompt from `GC-Move-OS-AI-Architecture.md` Section 4.

Call GPT-4o (not mini — quality matters here). Use function calling to ensure structured output.

Output stored in `recommendation_explanations`:
```python
class RecommendationOutput(BaseModel):
    executive_summary: str         # 2–3 sentence plain English summary
    why_it_fits: str               # Why this is recommended
    why_not_perfect: str           # Honest limitations
    what_to_verify: list[str]      # Action items before inspecting
    what_may_be_regretted: str     # Honest risk assessment
    ronnie_commentary: str
    susie_commentary: str
    austin_commentary: str
    mabel_commentary: str
    main_trade_off: str
    next_action: str               # Clear single next step
    five_year_prediction: str      # Long-term outcome narrative
    confidence_explanation: str    # Why confidence is this level
```

Done when: a full evaluation report is generated with all narrative fields populated and per-person commentary is specific and relevant.

**Task 3.8 — Evaluation Orchestrator**

`services/evaluation_orchestrator.py`:

Background task that runs all scoring services in sequence:

```python
async def run_evaluation(property_id: str, family_id: str, db: AsyncSession):
    # 1. Load property + family
    # 2. Run community scoring
    # 3. Run lifestyle scoring
    # 4. Run school scoring
    # 5. Run property scoring (AI-assisted)
    # 6. Run risk scoring
    # 7. Calculate financial score
    # 8. Calculate family fit score
    # 9. Determine recommendation level
    # 10. Calculate confidence score
    # 11. Generate AI recommendation narrative
    # 12. Calculate five-year fit score
    # 13. Generate per-member commentary
    # 14. Save PropertyEvaluation record
    # 15. Save EvaluationScore record
    # 16. Save RecommendationExplanation record
    # 17. Update Property.status = "evaluated"
    # 18. Create DecisionJournalEntry
    # 19. Trigger preference learning scan
```

Done when: submitting a URL results in a fully evaluated property with all scores and narrative within 60 seconds.

---

### PHASE 4 — FRONTEND CORE

All screen specs are in `GC-Move-OS-UX-Spec.md`. This phase implements the essential screens.

**Task 4.1 — Design System Setup**

- Configure `tailwind.config.ts` with custom colour tokens:
  ```
  ocean: #1A3C5E
  sand: #E8DCC8
  teal: #4A9B8E
  background: #FAFAF8
  ```
- Install and configure shadcn/ui components: `button`, `card`, `badge`, `dialog`, `input`, `label`, `select`, `separator`, `skeleton`, `tabs`, `textarea`, `toast`
- Create custom score components (not in shadcn): `ScoreRing`, `FamilyFitScore`, `CategoryScoreRow`
- Done when: Storybook (optional) or a `/design-system` dev page shows all components

**Task 4.2 — API Client Layer**

`lib/api/client.ts`:
```typescript
const API_BASE = process.env.NEXT_PUBLIC_API_URL

export async function apiCall<T>(
  path: string,
  options: RequestInit & { token: string }
): Promise<T> {
  const { token, ...fetchOptions } = options
  const res = await fetch(`${API_BASE}${path}`, {
    ...fetchOptions,
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`,
      ...fetchOptions.headers,
    },
  })
  if (!res.ok) throw new ApiError(res.status, await res.json())
  return res.json()
}
```

Create typed functions for every endpoint from the API contract in `GC-Move-OS-Technical-Architecture.md`.

**Task 4.3 — Onboarding Flow**

Route: `/onboarding`

5-step wizard with progress indicator. See `GC-Move-OS-UX-Spec.md` Section 3 for detailed screen specs.

State management: Zustand store that accumulates onboarding data across steps before final submit.

Step completion triggers `POST /api/families` then `POST /api/families/{id}/members` for each family member.

After completion: redirect to `/app/dashboard` with `?onboarding=complete` query param (triggers welcome modal).

**Task 4.4 — Dashboard**

Route: `/app/dashboard`

Data from `GET /api/dashboard`:
- Top 3 recommendations (Prioritise Immediately first, then Inspect)
- Properties reviewed count
- New properties this week
- Shortlist count
- Recent journal entries

Layout: Left sidebar nav + main content area. See UX Spec for exact layout.

Key component: `PropertyCard` with `RecommendationBadge`, `FamilyFitScore`, and `CategoryScoreRow`.

**Task 4.5 — Property Submission**

Route: `/app/properties/new`

URL input with validation. Shows loading state during AI extraction (typically 10–20 seconds). Polls `GET /api/properties/{id}` every 3 seconds until `status !== "ingesting"`.

On completion: redirect to `/app/properties/{id}` (evaluation report).

**Task 4.6 — Property Evaluation Report**

Route: `/app/properties/[id]`

This is the most important screen. See UX Spec Section 3 for full spec.

Layout (top to bottom):
1. Property header (address, price, listing link)
2. `RecommendationBadge` + `FamilyFitScore` (large, prominent)
3. `ConfidenceIndicator`
4. `CategoryScoreRow` (Community / Lifestyle / School / Property / Financial)
5. Executive summary (AI-generated)
6. Risk flags
7. Family member cards (Ronnie / Susie / Austin / Mabel)
8. Trade-off panel
9. "What to Verify" checklist
10. "What You May Regret" section
11. Five-Year Fit Score + narrative
12. Action buttons: Save / Reject / Book Inspection / Ask Advisor

**Task 4.7 — Shortlist**

Route: `/app/shortlist`

Grid of saved properties. Comparison mode (select 2–3, side-by-side view). Sort by Family Fit Score.

**Task 4.8 — Property List**

Route: `/app/properties`

All submitted properties with status. Filter by recommendation level. Sort by score/date.

---

### PHASE 5 — AI ADVISOR

**Task 5.1 — Advisor Thread Management**

Backend:
- `POST /api/advisor/chat` — send message, get response
- `GET /api/advisor/history` — load thread history
- Thread is stored in `ai_advisor_threads` and `ai_advisor_messages`
- One thread per family (or per session — use one thread for MVP)

Family context injection: before every AI call, serialise family context from `GC-Move-OS-AI-Architecture.md` Section 10. Include:
- Family member profiles
- Top 5 confirmed preferences
- Current shortlist summary
- Recent decisions from journal

**Task 5.2 — Advisor Frontend**

Route: `/app/advisor`

Chat interface matching the spec in `GC-Move-OS-UX-Spec.md`.

Key UX decisions:
- Stream the AI response using `ReadableStream` from the API
- Show "thinking..." indicator while waiting
- Display `PreferenceCaptureTost` when AI detects a new preference signal in conversation
- Keep last 20 messages in view, load older on scroll

**Task 5.3 — Preference Capture from Conversation**

After every advisor response, trigger a background preference inference scan:
```python
async def extract_preference_signals_from_message(
    message: str, 
    family_id: str, 
    family_member_id: Optional[str]
) -> list[PreferenceSignal]:
    # Call GPT-4o-mini with preference extraction prompt
    # Return structured signals
    # Create PreferenceEvent records for each signal
```

---

### PHASE 6 — INTELLIGENCE FEATURES

**Task 6.1 — Suburb Intelligence**

Route: `/app/suburbs`  
Route: `/app/suburbs/[slug]`

List: All 16 Gold Coast suburbs with tier badge, Community Score, Lifestyle Score. Filter by tier.

Detail page: Full suburb profile with all scores, lifestyle assets, school proximity, suburb tier explanation, properties in this suburb.

**Task 6.2 — School Intelligence**

Route: `/app/schools`

Comparison page showing Somerset College and All Saints side by side. Score breakdown for each school. Commute calculator (enter property address, get drive time to each school).

**Task 6.3 — Preference Profile**

Route: `/app/preferences`

Visualise what the system has learned about the family. Show:
- "Things Ronnie Values" (top preferences by weight)
- "Things Susie Values"
- "The Family Consistently Rejects" (negative preferences)
- "Emerging Preferences" (low confidence, developing)
- "Confirmed Non-Negotiables"

Allow family to manually adjust weights or retire incorrect inferences.

**Task 6.4 — Decision Journal**

Route: `/app/journal`

Chronological list of all property decisions. Each entry shows: property thumbnail, decision (Inspect/Monitor/Ignore/Prioritise), date, key reasoning. Filter by decision type.

---

### PHASE 7 — POLISH & LAUNCH

**Task 7.1 — Inspection Tracker**

Route: `/app/inspections`

Create/edit inspections linked to properties. Fields: property, date/time, agent contact, notes, outcome. Status: Scheduled / Completed / Cancelled.

**Task 7.2 — Daily Brief Email**

Background job (Railway cron or simple scheduler): runs daily at 7:00 AM AEST.
- Fetches new properties that haven't been evaluated for this family
- Triggers evaluations
- Sends email via Resend with top 3 new recommendations
- Uses Resend React Email template

**Task 7.3 — Performance Optimisation**

- Cache suburb and school pages with Next.js ISR (revalidate: 86400)
- Prefetch property evaluation when user hovers over PropertyCard
- Add Redis caching for suburb scores (TTL: 24h) and travel times (TTL: 7 days)
- Lazy load property images
- Add `loading.tsx` for all route segments

**Task 7.4 — Monitoring Setup**

Sentry:
- Configure source maps upload in `next.config.ts`
- Add `Sentry.captureException` in API error handlers
- Add `Sentry.captureMessage` for AI failures (extraction failure, scoring failure)

PostHog:
- Track key events: `property_submitted`, `evaluation_viewed`, `property_saved`, `property_rejected`, `advisor_message_sent`, `inspection_created`, `journal_entry_created`
- Add user identification on sign-in: `posthog.identify(userId, { family_id })`

**Task 7.5 — Pre-Launch Checklist**

- [ ] All 16 suburbs seeded with accurate data
- [ ] Somerset College and All Saints seeded with accurate scores
- [ ] All non-negotiable filters working correctly
- [ ] AI extraction tested on 20+ real property URLs
- [ ] Scoring engine producing sensible results (spot check 10 properties)
- [ ] AI advisor coherent with family context
- [ ] Email notifications sending correctly
- [ ] Sentry receiving errors
- [ ] PostHog receiving events
- [ ] All routes protected by auth middleware
- [ ] Family data isolation verified (query all endpoints as wrong family_id, confirm 0 results)
- [ ] Mobile responsive layout checked on iPhone and iPad
- [ ] Performance: dashboard loads in under 2 seconds
- [ ] Performance: property evaluation visible within 60 seconds of URL submission

---

## 7. Key Implementation Rules

These rules apply across the entire codebase. Violating them creates technical debt.

**Rule 1 — Every query must be scoped to family_id**
```python
# WRONG
properties = await db.execute(select(Property))

# RIGHT  
properties = await db.execute(
    select(Property).where(
        Property.family_id == current_family_id,
        Property.deleted_at.is_(None)
    )
)
```

**Rule 2 — Soft deletes only**
Never `DELETE` records. Set `deleted_at = now()`. All queries must include `.where(Model.deleted_at.is_(None))`.

**Rule 3 — All AI calls must have a timeout and fallback**
```python
try:
    result = await openai_call_with_timeout(prompt, timeout=30)
except (TimeoutError, OpenAIError) as e:
    sentry_sdk.capture_exception(e)
    result = generate_fallback_result()  # Graceful degradation
```

**Rule 4 — Confidence scores reflect data completeness**
If suburb data is missing → reduce confidence by 0.15. If school catchment unknown → reduce by 0.10. If travel times not calculated → reduce by 0.10. If no images → reduce by 0.05. Never present low-confidence results as certain.

**Rule 5 — Critical risks always override scores**
A property with `has_critical_risk = True` must never receive `Prioritise Immediately` recommendation, regardless of score.

**Rule 6 — Every preference event must record its source**
```python
PreferenceEvent(
    source="ai_inferred",  # never blank
    evidence_text="User saved 3 properties with pool",  # always include evidence
    strength=3,  # always include strength
)
```

**Rule 7 — AI explanations must be specific, not generic**
Test every AI prompt by asking: "Could this explanation apply to a different property?" If yes, the prompt needs more specific family context injected.

**Rule 8 — TypeScript types must mirror Pydantic schemas exactly**
Create a shared types file or codegen step. Never let frontend and backend type definitions drift.

---

## 8. Testing Requirements

### Unit Tests (pytest for backend, Vitest for frontend)

**Backend critical test coverage**:
- `test_community_scoring.py`: verify Robina scores 7.5+
- `test_lifestyle_scoring.py`: verify travel time scoring function
- `test_family_fit.py`: verify formula and recommendation thresholds
- `test_risk_scoring.py`: verify critical risk blocks prioritise recommendation
- `test_non_negotiables.py`: verify each non-negotiable correctly gates properties
- `test_preference_learning.py`: verify 3+ consistent signals increase confidence
- `test_data_isolation.py`: verify family_id scoping on all queries

**Frontend critical test coverage**:
- `FamilyFitScore.test.tsx`: score displays correct colour for each band
- `RecommendationBadge.test.tsx`: correct label for each recommendation level
- `onboarding.test.tsx`: wizard advances correctly and submits family data

### Integration Tests

- Full property ingestion pipeline (mock OpenAI + Google Maps)
- Full evaluation pipeline (mock AI calls, use fixture suburb/school data)
- Advisor conversation thread (mock OpenAI)

### Acceptance Tests (manual for MVP)

Before considering any feature complete, verify:
1. As Ronnie: submit a real Gold Coast property URL → evaluation completes → recommendation makes sense
2. As Susie: use advisor to discuss a property → advisor references family preferences correctly
3. Check that Somerset College scores higher than a random state school in suburb comparison

---

## 9. Critical Path

The minimum path to a working MVP:

1. Phase 0 (auth + infra) — **blocker for everything**
2. Phase 1.1 + 1.2 (DB schema + migration) — **blocker for everything**
3. Phase 1.3 (seed data) — **blocker for scoring**
4. Phase 2.1–2.3 (URL ingestion + AI extraction) — **blocker for scoring**
5. Phase 3.7 + 3.8 (AI recommendation + orchestrator) — **blocker for useful output**
6. Phase 4.5 + 4.6 (property submission + evaluation report) — **first usable screen**
7. Phase 5 (AI advisor) — **core intelligence feature**

Everything else enhances the experience but does not block core use.

---

## 10. Open Questions (Resolve Before Build)

| ID | Question | Priority | Impact |
|---|---|---|---|
| OQ-001 | What is the family budget (BudgetMin / BudgetMax)? | Critical | Captured in Family Inputs page (editable any time). Financial score disabled until set. |
| OQ-002 | Confirm Apify actor IDs for REA and Domain. Test both against 5 real Gold Coast URLs in Apify console. Note exact field names returned. | Critical | Property ingestion cannot begin without confirmed, tested actor IDs. |
| OQ-003 | **RESOLVED** — Susie has her own Clerk account linked to the family via `family_users` table. Invite flow is in MVP scope. | Resolved | Multi-user family model confirmed. |
| OQ-004 | Which OpenAI pricing tier are we on? | Medium | ~$0.09 per evaluation at standard pricing |
| OQ-005 | Google Maps API key and billing enabled? | High | Travel times blocked without this |
| OQ-006 | Resend account set up? Domain verified for sending? | Medium | Email invite + daily brief blocked |
| OQ-007 | What suburb data source for ABS census fields? Use 2021 census CSV download or third-party API? | High | Community scores cannot be calculated without this |
| OQ-008 | Should the product be private (Altit family only) or open to a small beta list? | Medium | Affects Clerk onboarding flow — open registration vs. invite-only |
| OQ-009 | What is the Apify per-scrape cost at expected MVP volume? Confirm pricing before launch. | Medium | Budget for scraping costs |
| OQ-010 | PropTrack API — is a partnership in scope for Phase 2, or later? | Low | Affects Phase 2 planning only |

---

## 11. Companion Documents

Refer to these documents throughout development:

| Document | Use When |
|---|---|
| `GC-Move-OS-PRD.md` | Deciding what a feature should do; checking user stories; acceptance criteria |
| `GC-Move-OS-UX-Spec.md` | Implementing any screen; confirming layout, component states, interactions |
| `GC-Move-OS-Technical-Architecture.md` | API contracts, folder structure, infrastructure setup |
| `GC-Move-OS-AI-Architecture.md` | Writing any AI prompt; function calling schemas; cost estimates |
| `GC-Move-OS-Data-Architecture.md` | Understanding external data sources; pipeline design; caching strategy |
| `GC-Move-OS-Database-Design.md` | Writing SQL queries; creating migrations; understanding table structure |

---

## 12. Definition of Done

A feature is complete when:
1. Backend endpoint(s) implemented and returning correct data
2. Frontend screen(s) implemented matching UX Spec
3. Unit tests pass
4. Feature works end-to-end in local development
5. No TypeScript errors (`tsc --noEmit` passes)
6. No ESLint errors
7. Sentry error tracking confirmed (trigger an error in dev, verify it appears in Sentry)
8. Key PostHog event fires when feature is used

---

*End of Gold Coast Move OS Build Pack v1.0*
