# Gold Coast Move OS — Technical Architecture
**Document 3 of 7 | Version 1.0 | June 2026**

---

## 1. System Overview

### 1.1 Architecture Philosophy

Gold Coast Move OS is a request-response platform with asynchronous AI evaluation at its core. The architecture is deliberately boring at the infrastructure layer (Next.js + FastAPI + PostgreSQL) so the team can focus engineering effort on the intelligence layer. No microservices in MVP. No event streaming. One backend, one database, one cache, one queue-equivalent (FastAPI BackgroundTasks). Complexity is added only when a specific bottleneck demands it.

### 1.2 High-Level Component Map

```
┌─────────────────────────────────────────────────────────────────────┐
│                          USER BROWSER                               │
│                     Next.js 14 (App Router)                         │
│              Vercel Edge + CDN | clerk.com auth layer               │
└───────────────────────────┬─────────────────────────────────────────┘
                            │ HTTPS / REST
                            ▼
┌─────────────────────────────────────────────────────────────────────┐
│                     FastAPI Backend (Railway)                        │
│                                                                     │
│  ┌─────────────┐  ┌──────────────┐  ┌──────────────────────────┐  │
│  │   Routers   │  │  Service     │  │  Background Tasks        │  │
│  │  (domains)  │→ │  Layer       │→ │  (evaluation pipeline)   │  │
│  └─────────────┘  └──────────────┘  └──────────────────────────┘  │
│                          │                                          │
│               ┌──────────┴──────────┐                              │
│               ▼                     ▼                              │
│  ┌────────────────────┐  ┌─────────────────────┐                  │
│  │  PostgreSQL 15     │  │  Redis Cache         │                  │
│  │  (Railway)         │  │  (Railway)           │                  │
│  └────────────────────┘  └─────────────────────┘                  │
└─────────────────────────────────────────────────────────────────────┘
                            │
              ┌─────────────┼──────────────┐
              ▼             ▼              ▼
      ┌──────────────┐ ┌──────────┐ ┌────────────┐
      │  OpenAI API  │ │ Google   │ │ Cloudinary │
      │  GPT-4o      │ │ Maps API │ │ (images)   │
      └──────────────┘ └──────────┘ └────────────┘
```

### 1.3 Request Flow: Standard API Call

```
1. User action in browser (e.g. submits property URL)
2. Next.js calls its own API route (/api/... → /app/api/route.ts)
3. API route reads Clerk session token
4. API route forwards request to FastAPI with Authorization: Bearer <clerk_jwt>
5. FastAPI middleware verifies JWT with Clerk JWKS endpoint
6. FastAPI extracts clerk_user_id, looks up internal family_id
7. Router delegates to service layer
8. Service reads/writes PostgreSQL via SQLAlchemy async
9. Heavy tasks (AI evaluation) dispatched to BackgroundTasks
10. FastAPI returns 202 Accepted with evaluation_id
11. Frontend polls GET /api/evaluations/{id} every 3s until status = complete
12. Complete evaluation result rendered to user
```

### 1.4 Request Flow: Property Evaluation (Async)

```
POST /api/properties/ingest
  → validate URL (realestate.com.au or domain.com.au pattern)
  → submit URL to Apify actor (via apify-client Python SDK)
  → Apify returns structured JSON (address, price, bedrooms, bathrooms, features, images, description)
  → persist Property record with Apify data (status=ingested)
  → enqueue background task: run_evaluation(property_id, family_id)
  → return {property_id, evaluation_id, status: "processing"}

Background Task:
  → fetch suburb data (Redis cache or DB)
  → fetch school catchment
  → call Google Maps Distance Matrix
  → run scoring services
  → call OpenAI for narrative generation
  → persist PropertyEvaluation (status=complete)
  → trigger Resend notification email (optional)

Frontend:
  → poll GET /api/evaluations/{id}
  → on status=complete: render full evaluation
```

---

## 2. Frontend Architecture (Next.js 14)

### 2.1 Folder Structure

```
src/
├── app/
│   ├── layout.tsx                    # Root layout: ClerkProvider, QueryProvider, Toaster
│   ├── page.tsx                      # Landing / marketing page
│   ├── (auth)/
│   │   ├── sign-in/[[...sign-in]]/page.tsx
│   │   └── sign-up/[[...sign-up]]/page.tsx
│   ├── (dashboard)/
│   │   ├── layout.tsx                # Authenticated shell: sidebar, header
│   │   ├── dashboard/page.tsx        # Home: recommendations, activity feed
│   │   ├── properties/
│   │   │   ├── page.tsx              # Property list with filters
│   │   │   ├── [id]/page.tsx         # Full property evaluation view
│   │   │   └── add/page.tsx          # URL submission form
│   │   ├── suburbs/
│   │   │   ├── page.tsx              # Suburb comparison grid
│   │   │   └── [id]/page.tsx         # Suburb deep-dive
│   │   ├── schools/
│   │   │   ├── page.tsx              # School comparison
│   │   │   └── [id]/page.tsx         # School profile
│   │   ├── shortlist/page.tsx        # Saved properties
│   │   ├── advisor/page.tsx          # AI chat interface
│   │   ├── journal/page.tsx          # Decision journal
│   │   ├── inspections/
│   │   │   ├── page.tsx              # Inspection calendar/list
│   │   │   └── [id]/page.tsx         # Inspection detail
│   │   └── profile/page.tsx          # Family profile + preferences
│   └── api/
│       ├── families/route.ts
│       ├── families/[id]/route.ts
│       ├── properties/route.ts
│       ├── properties/ingest/route.ts
│       ├── properties/[id]/route.ts
│       ├── evaluations/route.ts
│       ├── evaluations/[id]/route.ts
│       ├── suburbs/route.ts
│       ├── suburbs/[id]/route.ts
│       ├── schools/route.ts
│       ├── schools/[id]/route.ts
│       ├── advisor/chat/route.ts
│       ├── advisor/history/route.ts
│       ├── journal/route.ts
│       ├── preferences/route.ts
│       ├── inspections/route.ts
│       └── dashboard/route.ts
├── components/
│   ├── ui/                           # shadcn/ui primitives (auto-generated)
│   ├── layout/
│   │   ├── Sidebar.tsx
│   │   ├── Header.tsx
│   │   └── MobileNav.tsx
│   ├── property/
│   │   ├── PropertyCard.tsx
│   │   ├── PropertyURLForm.tsx
│   │   ├── PropertyEvaluationPanel.tsx
│   │   ├── ScoreBreakdown.tsx
│   │   ├── FamilyMemberImpact.tsx
│   │   ├── TradeOffList.tsx
│   │   ├── VerifyChecklist.tsx
│   │   └── RecommendationBadge.tsx
│   ├── suburb/
│   │   ├── SuburbCard.tsx
│   │   └── SuburbScoreGrid.tsx
│   ├── school/
│   │   ├── SchoolCard.tsx
│   │   └── SchoolCompareTable.tsx
│   ├── advisor/
│   │   ├── ChatInterface.tsx
│   │   ├── ChatMessage.tsx
│   │   └── SuggestedPrompts.tsx
│   ├── journal/
│   │   ├── JournalEntry.tsx
│   │   └── JournalTimeline.tsx
│   ├── dashboard/
│   │   ├── RecommendationFeed.tsx
│   │   ├── ActivityFeed.tsx
│   │   └── FitScoreGauge.tsx
│   └── shared/
│       ├── ConfidenceBadge.tsx
│       ├── ScorePill.tsx
│       ├── LoadingEvaluation.tsx
│       └── ErrorBoundary.tsx
├── lib/
│   ├── api-client.ts                 # Typed fetch wrapper
│   ├── query-keys.ts                 # React Query key factory
│   ├── utils.ts                      # cn(), formatScore(), etc.
│   └── constants.ts
├── hooks/
│   ├── useFamily.ts
│   ├── useEvaluation.ts              # includes polling logic
│   ├── useProperties.ts
│   ├── useAdvisor.ts
│   └── usePreferences.ts
├── store/
│   └── ui-store.ts                   # Zustand: sidebar state, active filters, modal state
├── types/
│   ├── api.ts                        # All request/response types
│   ├── domain.ts                     # Domain model types
│   └── scoring.ts                    # Score types
└── styles/
    └── globals.css
```

### 2.2 Route Definitions

| Route | Purpose |
|---|---|
| `/` | Landing page, sign up CTA |
| `/sign-in` | Clerk hosted sign-in |
| `/sign-up` | Clerk hosted sign-up |
| `/dashboard` | Main hub: top recommendations, recent activity, fit score summary |
| `/properties` | All ingested properties with status filters (saved, rejected, monitoring) |
| `/properties/add` | URL paste form for property ingestion |
| `/properties/[id]` | Full evaluation view: scores, narratives, per-person impact, next actions |
| `/suburbs` | Suburb comparison across Gold Coast areas |
| `/suburbs/[id]` | Suburb deep-dive: community data, lifestyle score, school ecosystem |
| `/schools` | School comparison with catchment map |
| `/schools/[id]` | School profile: wellbeing, community, academic scores |
| `/shortlist` | Saved/shortlisted properties with side-by-side compare |
| `/advisor` | Persistent AI chat with memory of all properties and preferences |
| `/journal` | Decision journal timeline |
| `/inspections` | Inspection log and schedule |
| `/profile` | Family members, preferences, non-negotiables |

### 2.3 State Management

**React Query (TanStack Query v5)** handles all server state: fetching, caching, background refetch, optimistic updates, and the evaluation polling loop. This is the dominant state layer.

**Zustand** handles client-only UI state: sidebar collapsed/expanded, active filter state, modal open/closed, active comparison set.

No Redux. No Context API for data (only for theme/auth which Clerk handles). If it came from the server, it's React Query. If it exists only in the browser, it's Zustand.

```typescript
// lib/query-keys.ts
export const queryKeys = {
  family: (id: string) => ['family', id] as const,
  properties: (familyId: string, filters?: PropertyFilters) => ['properties', familyId, filters] as const,
  property: (id: string) => ['property', id] as const,
  evaluation: (id: string) => ['evaluation', id] as const,
  evaluationsByFamily: (familyId: string) => ['evaluations', 'family', familyId] as const,
  suburbs: () => ['suburbs'] as const,
  suburb: (id: string) => ['suburb', id] as const,
  schools: (suburbId?: string) => ['schools', suburbId] as const,
  school: (id: string) => ['school', id] as const,
  dashboard: (familyId: string) => ['dashboard', familyId] as const,
  advisorHistory: (familyId: string) => ['advisor', 'history', familyId] as const,
  journal: (familyId: string) => ['journal', familyId] as const,
  preferences: (familyId: string) => ['preferences', familyId] as const,
}
```

### 2.4 Evaluation Polling Hook

```typescript
// hooks/useEvaluation.ts
export function useEvaluation(evaluationId: string | null) {
  return useQuery({
    queryKey: queryKeys.evaluation(evaluationId ?? ''),
    queryFn: () => apiClient.get<EvaluationResponse>(`/evaluations/${evaluationId}`),
    enabled: !!evaluationId,
    refetchInterval: (data) => {
      if (!data) return 3000
      if (data.status === 'processing' || data.status === 'queued') return 3000
      return false // Stop polling when complete or failed
    },
    staleTime: Infinity, // Don't background-refetch completed evaluations
  })
}
```

### 2.5 API Client Layer

All calls to the FastAPI backend go through a typed wrapper. Next.js API routes act as a thin BFF (Backend for Frontend), injecting the Clerk JWT before forwarding to FastAPI.

```typescript
// lib/api-client.ts
import { auth } from '@clerk/nextjs/server'

async function fetchWithAuth(path: string, options?: RequestInit) {
  const { getToken } = auth()
  const token = await getToken()

  const res = await fetch(`${process.env.FASTAPI_URL}${path}`, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${token}`,
      ...options?.headers,
    },
  })

  if (!res.ok) {
    const error = await res.json().catch(() => ({ detail: 'Unknown error' }))
    throw new APIError(res.status, error.detail)
  }

  return res.json()
}

export const apiClient = {
  get: <T>(path: string) => fetchWithAuth(path) as Promise<T>,
  post: <T>(path: string, body: unknown) =>
    fetchWithAuth(path, { method: 'POST', body: JSON.stringify(body) }) as Promise<T>,
  put: <T>(path: string, body: unknown) =>
    fetchWithAuth(path, { method: 'PUT', body: JSON.stringify(body) }) as Promise<T>,
  delete: <T>(path: string) =>
    fetchWithAuth(path, { method: 'DELETE' }) as Promise<T>,
}
```

### 2.6 Authentication (Clerk)

Clerk handles all auth. The `(dashboard)` route group wraps every authenticated page in a layout that uses `<ClerkProvider>` and checks session server-side.

```typescript
// app/(dashboard)/layout.tsx
import { auth } from '@clerk/nextjs/server'
import { redirect } from 'next/navigation'

export default async function DashboardLayout({ children }: { children: React.ReactNode }) {
  const { userId } = auth()
  if (!userId) redirect('/sign-in')
  return <>{children}</>
}
```

Clerk middleware (`middleware.ts`) protects all `/dashboard`, `/properties`, `/advisor`, etc. routes at the edge. Public routes: `/`, `/sign-in`, `/sign-up`.

### 2.7 Environment Variables (Frontend)

```bash
# .env.local
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=pk_...
CLERK_SECRET_KEY=sk_...
NEXT_PUBLIC_CLERK_SIGN_IN_URL=/sign-in
NEXT_PUBLIC_CLERK_SIGN_UP_URL=/sign-up
NEXT_PUBLIC_CLERK_AFTER_SIGN_IN_URL=/dashboard
NEXT_PUBLIC_CLERK_AFTER_SIGN_UP_URL=/dashboard

FASTAPI_URL=https://gcmove-api.railway.app   # Internal: not exposed to browser
NEXT_PUBLIC_POSTHOG_KEY=phc_...
NEXT_PUBLIC_POSTHOG_HOST=https://app.posthog.com
NEXT_PUBLIC_SENTRY_DSN=https://...
```

---

## 3. Backend Architecture (FastAPI)

### 3.1 Folder Structure

```
backend/
├── main.py                           # App factory, middleware, router registration
├── config.py                         # Settings via pydantic-settings
├── database.py                       # AsyncEngine, SessionLocal, Base
├── dependencies.py                   # get_db(), get_current_family(), verify_clerk_jwt()
├── routers/
│   ├── families.py                   # /families/*
│   ├── properties.py                 # /properties/*
│   ├── evaluations.py                # /evaluations/*
│   ├── suburbs.py                    # /suburbs/*
│   ├── schools.py                    # /schools/*
│   ├── advisor.py                    # /advisor/*
│   ├── journal.py                    # /journal/*
│   ├── preferences.py                # /preferences/*
│   ├── inspections.py                # /inspections/*
│   └── dashboard.py                  # /dashboard
├── services/
│   ├── property_ingestion.py         # URL fetch, OpenAI extraction
│   ├── property_scoring.py           # PropertyScoringService
│   ├── community_scoring.py          # CommunityScoringService
│   ├── lifestyle_scoring.py          # LifestyleScoringService
│   ├── school_scoring.py             # SchoolScoringService
│   ├── risk_scoring.py               # RiskScoringService
│   ├── family_fit.py                 # FamilyFitService (weighted aggregation)
│   ├── five_year_prediction.py       # FiveYearFitService
│   ├── recommendation.py             # RecommendationService
│   ├── explainability.py             # ExplainabilityService
│   ├── memory.py                     # MemoryService
│   ├── preference_learning.py        # PreferenceLearningService
│   ├── decision_journal.py           # DecisionJournalService
│   ├── advisor.py                    # AI advisor chat
│   ├── travel_time.py                # Google Maps Distance Matrix
│   ├── school_catchment.py           # Catchment lookup
│   └── notification.py               # Resend email
├── models/
│   ├── family.py                     # SQLAlchemy ORM models
│   ├── property.py
│   ├── suburb.py
│   ├── school.py
│   ├── evaluation.py
│   ├── memory.py
│   ├── preference.py
│   ├── journal.py
│   ├── inspection.py
│   └── audit.py
├── schemas/
│   ├── family.py                     # Pydantic request/response schemas
│   ├── property.py
│   ├── suburb.py
│   ├── school.py
│   ├── evaluation.py
│   ├── advisor.py
│   ├── journal.py
│   ├── preference.py
│   └── dashboard.py
├── migrations/
│   ├── env.py
│   └── versions/
├── tasks/
│   └── evaluation_pipeline.py        # Full async evaluation orchestrator
├── utils/
│   ├── redis_client.py
│   ├── openai_client.py
│   ├── clerk_auth.py
│   └── url_validator.py
└── tests/
    ├── test_routers/
    ├── test_services/
    └── conftest.py
```

### 3.2 Application Factory

```python
# main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from routers import families, properties, evaluations, suburbs, schools, advisor, journal, preferences, inspections, dashboard

@asynccontextmanager
async def lifespan(app: FastAPI):
    # startup: initialise Redis connection pool
    yield
    # shutdown: close connections

app = FastAPI(title="GC Move OS API", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_URL],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(families.router, prefix="/api/families", tags=["families"])
app.include_router(properties.router, prefix="/api/properties", tags=["properties"])
app.include_router(evaluations.router, prefix="/api/evaluations", tags=["evaluations"])
app.include_router(suburbs.router, prefix="/api/suburbs", tags=["suburbs"])
app.include_router(schools.router, prefix="/api/schools", tags=["schools"])
app.include_router(advisor.router, prefix="/api/advisor", tags=["advisor"])
app.include_router(journal.router, prefix="/api/journal", tags=["journal"])
app.include_router(preferences.router, prefix="/api/preferences", tags=["preferences"])
app.include_router(inspections.router, prefix="/api/inspections", tags=["inspections"])
app.include_router(dashboard.router, prefix="/api/dashboard", tags=["dashboard"])

@app.get("/health")
async def health_check():
    return {"status": "ok", "version": "1.0.0"}
```

### 3.3 Auth Middleware

```python
# utils/clerk_auth.py
import httpx
import jwt
from fastapi import HTTPException, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

security = HTTPBearer()

async def verify_clerk_jwt(credentials: HTTPAuthorizationCredentials = Security(security)) -> str:
    token = credentials.credentials
    try:
        # Clerk JWKS endpoint
        jwks = await get_clerk_jwks()
        header = jwt.get_unverified_header(token)
        key = next(k for k in jwks['keys'] if k['kid'] == header['kid'])
        public_key = jwt.algorithms.RSAAlgorithm.from_jwk(key)
        payload = jwt.decode(token, public_key, algorithms=["RS256"], audience=settings.CLERK_AUDIENCE)
        return payload['sub']  # clerk_user_id
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

# dependencies.py
# Multi-user family model: a Clerk user is linked to a family via the family_users table.
# Multiple users can belong to the same family (e.g., Ronnie and Susie).
# Each user has their own Clerk account but shares all family data.

async def get_current_user_and_family(
    clerk_user_id: str = Depends(verify_clerk_jwt),
    db: AsyncSession = Depends(get_db)
) -> tuple[FamilyUser, Family]:
    """
    Resolve: Clerk user ID → FamilyUser → Family
    Returns both the current user record (for per-user preference tracking)
    and the family record (for shared family data).
    """
    result = await db.execute(
        select(FamilyUser, Family)
        .join(Family, FamilyUser.family_id == Family.id)
        .where(
            FamilyUser.clerk_user_id == clerk_user_id,
            FamilyUser.deleted_at.is_(None),
            Family.deleted_at.is_(None)
        )
    )
    row = result.first()
    if not row:
        raise HTTPException(status_code=404, detail="User not linked to a family profile")
    return row.FamilyUser, row.Family

# Convenience dependency for routes that only need the family
async def get_current_family(
    user_and_family: tuple = Depends(get_current_user_and_family)
) -> Family:
    _, family = user_and_family
    return family

# Convenience dependency for routes that need the current user (for per-user preference capture)
async def get_current_family_user(
    user_and_family: tuple = Depends(get_current_user_and_family)
) -> FamilyUser:
    user, _ = user_and_family
    return user
```

### 3.4 Database Access Pattern

All database access uses SQLAlchemy 2.0 async with `AsyncSession`. Never use sync sessions. All queries must include `family_id` as a filter condition — this is the primary data isolation mechanism.

```python
# database.py
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

engine = create_async_engine(settings.DATABASE_URL, echo=False, pool_size=10, max_overflow=20)
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)

async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
```

### 3.5 Service Layer Pattern

Services receive a database session and return domain objects or Pydantic schemas. They are never called directly by route handlers without going through the dependency layer. This makes services independently testable.

```python
# services/property_scoring.py
class PropertyScoringService:
    def __init__(self, db: AsyncSession, openai_client: AsyncOpenAI):
        self.db = db
        self.openai = openai_client

    async def score(self, property: Property, family: Family) -> PropertyScoreResult:
        # Deterministic sub-scores from structured data
        modernity_score = self._score_modernity(property)
        indoor_outdoor_score = self._score_indoor_outdoor(property)
        pool_score = self._score_pool(property)
        office_score = self._score_office(property)
        privacy_score = self._score_privacy(property)
        entertaining_score = self._score_entertaining(property)

        raw_score = (
            modernity_score * 0.25 +
            indoor_outdoor_score * 0.20 +
            pool_score * 0.15 +
            office_score * 0.15 +
            privacy_score * 0.15 +
            entertaining_score * 0.10
        )

        # AI generates narrative commentary, not the score
        commentary = await self._generate_commentary(property, family, raw_score)

        return PropertyScoreResult(
            score=round(raw_score * 100),
            sub_scores={
                "modernity": modernity_score,
                "indoor_outdoor": indoor_outdoor_score,
                "pool": pool_score,
                "office": office_score,
                "privacy": privacy_score,
                "entertaining": entertaining_score,
            },
            commentary=commentary
        )
```

### 3.6 Background Task Handling

FastAPI BackgroundTasks is used for the evaluation pipeline. This avoids the need for a separate task queue (Celery, etc.) at MVP scale. Railway keeps the process alive. If evaluation volume exceeds 50 concurrent at peak, migrate to a proper queue.

```python
# routers/properties.py
@router.post("/ingest", status_code=202)
async def ingest_property(
    request: PropertyIngestRequest,
    background_tasks: BackgroundTasks,
    family: Family = Depends(get_current_family),
    db: AsyncSession = Depends(get_db),
):
    url_validator.validate(request.url)
    property_id = await PropertyIngestionService(db).create_pending(request.url, family.id)
    evaluation_id = await EvaluationService(db).create_pending(property_id, family.id)

    background_tasks.add_task(
        run_evaluation_pipeline,
        property_id=property_id,
        evaluation_id=evaluation_id,
        family_id=family.id,
    )

    return {"property_id": property_id, "evaluation_id": evaluation_id, "status": "processing"}
```

### 3.7 Caching Strategy (Redis)

Suburb and school data is static on a daily basis. Cache aggressively. Cache keys include the entity ID and a date stamp so cache invalidation is predictable.

```python
# utils/redis_client.py
SUBURB_CACHE_TTL = 86400      # 24 hours
SCHOOL_CACHE_TTL = 86400      # 24 hours
TRAVEL_TIME_CACHE_TTL = 3600  # 1 hour (traffic patterns shift)
OPENAI_EXTRACTION_CACHE = 0   # Never cache; listings change

async def get_suburb_cached(suburb_id: str) -> SuburbData | None:
    key = f"suburb:{suburb_id}"
    cached = await redis.get(key)
    if cached:
        return SuburbData.model_validate_json(cached)
    return None

async def set_suburb_cached(suburb_id: str, data: SuburbData):
    key = f"suburb:{suburb_id}"
    await redis.setex(key, SUBURB_CACHE_TTL, data.model_dump_json())
```

### 3.8 Rate Limiting

AI endpoints are expensive. Rate limit the advisor chat and evaluation trigger endpoints. Use a Redis-backed sliding window counter.

```python
# middleware: max 10 AI advisor messages per hour per family
# middleware: max 20 property evaluations per day per family
# middleware: max 100 general API requests per minute per family
```

### 3.9 Environment Variables (Backend)

```bash
# Railway environment variables
DATABASE_URL=postgresql+asyncpg://user:pass@host:5432/gcmove
REDIS_URL=redis://default:pass@host:6379

CLERK_SECRET_KEY=sk_...
CLERK_JWKS_URL=https://[clerk-domain]/.well-known/jwks.json
CLERK_AUDIENCE=

OPENAI_API_KEY=sk-proj-...
OPENAI_DEFAULT_MODEL=gpt-4o
OPENAI_FAST_MODEL=gpt-4o-mini

APIFY_API_TOKEN=apify_api_...
APIFY_REA_ACTOR_ID=           # e.g. "apify/realestate-com-au-scraper" — confirm before build
APIFY_DOMAIN_ACTOR_ID=        # e.g. "apify/domain-com-au-scraper" — confirm before build

GOOGLE_MAPS_API_KEY=AIza...
CLOUDINARY_URL=cloudinary://...
RESEND_API_KEY=re_...

FRONTEND_URL=https://gcmove.vercel.app
SENTRY_DSN=https://...

BURLEIGH_COORDS="-28.0853,153.4565"
NEAREST_BEACH_BURLEIGH="-28.0744,153.4573"
```

---

## 4. API Contract

### 4.1 Schema Conventions

All request/response bodies are JSON. Auth header: `Authorization: Bearer <clerk_jwt>`. All timestamps: ISO 8601. All scores: integers 0–100. Confidence: float 0.0–1.0.

### 4.2 Error Response Format

```typescript
interface ErrorResponse {
  detail: string
  code?: string         // machine-readable error code
  field?: string        // for validation errors
}
```

Standard HTTP codes: 200 OK, 201 Created, 202 Accepted, 400 Bad Request, 401 Unauthorized, 403 Forbidden, 404 Not Found, 422 Unprocessable Entity, 429 Too Many Requests, 500 Internal Server Error.

---

### POST /api/families
Create family profile (called once after sign-up).

**Auth required:** Yes

**Request:**
```typescript
interface CreateFamilyRequest {
  family_name: string
  current_location: string
  target_region: string           // e.g. "Gold Coast"
  budget_min: number
  budget_max: number
  move_timeframe: string          // e.g. "6-12 months"
  primary_success_metric?: string
}
```

**Response 201:**
```typescript
interface FamilyResponse {
  id: string
  family_name: string
  current_location: string
  target_region: string
  budget_min: number
  budget_max: number
  move_timeframe: string
  created_at: string
}
```

**Errors:** 400 (validation), 409 (family already exists for this user)

---

### GET /api/families/{id}
**Auth required:** Yes (must own family)

**Response 200:**
```typescript
interface FamilyDetailResponse extends FamilyResponse {
  members: FamilyMemberResponse[]
  preferences_count: number
  memories_count: number
}
```

**Errors:** 404, 403

---

### PUT /api/families/{id}
**Auth required:** Yes

**Request:**
```typescript
interface UpdateFamilyRequest {
  family_name?: string
  budget_min?: number
  budget_max?: number
  move_timeframe?: string
  primary_success_metric?: string
}
```

**Response 200:** Updated `FamilyResponse`

---

### POST /api/families/{id}/members
**Auth required:** Yes

**Request:**
```typescript
interface CreateFamilyMemberRequest {
  name: string
  role: 'Parent' | 'Child' | 'Pet' | 'OtherDependent'
  age?: number
  life_stage?: string
  primary_priorities?: string[]
  secondary_priorities?: string[]
  non_negotiables?: string[]
}
```

**Response 201:**
```typescript
interface FamilyMemberResponse {
  id: string
  family_id: string
  name: string
  role: string
  age?: number
  primary_priorities: string[]
  secondary_priorities: string[]
  non_negotiables: string[]
  created_at: string
}
```

---

### POST /api/properties/ingest
Submit a listing URL for extraction and evaluation.

**Auth required:** Yes

**Request:**
```typescript
interface PropertyIngestRequest {
  url: string       // Must be realestate.com.au or domain.com.au
  notes?: string    // Optional user notes at submission time
}
```

**Response 202:**
```typescript
interface IngestAcceptedResponse {
  property_id: string
  evaluation_id: string
  status: 'processing'
  message: string
}
```

**Errors:** 400 (invalid URL domain), 429 (rate limit)

---

### GET /api/properties/{id}
**Auth required:** Yes

**Response 200:**
```typescript
interface PropertyResponse {
  id: string
  family_id: string
  address: string
  suburb_id: string
  suburb_name: string
  price_guide?: number
  price_guide_display?: string
  bedrooms?: number
  bathrooms?: number
  car_spaces?: number
  land_size?: number
  property_type: string
  listing_status: string
  source_url: string
  features: PropertyFeature[]
  images: string[]
  extraction_confidence: number
  status: 'ingested' | 'scoring' | 'complete' | 'failed'
  user_status?: 'saved' | 'rejected' | 'monitoring' | null
  created_at: string
  updated_at: string
}

interface PropertyFeature {
  name: string
  value: string | boolean | number
}
```

**Errors:** 404, 403

---

### GET /api/properties
**Auth required:** Yes

**Query parameters:**
```typescript
interface PropertyListParams {
  status?: 'saved' | 'rejected' | 'monitoring' | 'all'
  suburb_id?: string
  min_score?: number
  recommendation?: 'PrioritiseImmediately' | 'Inspect' | 'Monitor' | 'Ignore'
  page?: number
  page_size?: number   // default 20, max 50
}
```

**Response 200:**
```typescript
interface PropertyListResponse {
  items: PropertyListItem[]
  total: number
  page: number
  page_size: number
}

interface PropertyListItem {
  id: string
  address: string
  suburb_name: string
  price_guide_display?: string
  bedrooms?: number
  primary_image?: string
  family_fit_score?: number
  recommendation?: string
  user_status?: string
  created_at: string
}
```

---

### POST /api/evaluations
Manually trigger a re-evaluation of an existing property.

**Auth required:** Yes

**Request:**
```typescript
interface TriggerEvaluationRequest {
  property_id: string
}
```

**Response 202:**
```typescript
interface EvaluationAcceptedResponse {
  evaluation_id: string
  status: 'processing'
}
```

---

### GET /api/evaluations/{id}
**Auth required:** Yes

**Response 200:**
```typescript
interface EvaluationResponse {
  id: string
  property_id: string
  family_id: string
  status: 'queued' | 'processing' | 'complete' | 'failed'

  // Only present when status = complete
  family_fit_score?: number
  five_year_fit_score?: number
  confidence_score?: number
  confidence_label?: 'Low' | 'Moderate' | 'High' | 'Very High'
  recommendation?: 'PrioritiseImmediately' | 'Inspect' | 'Monitor' | 'Ignore'

  community_score?: number
  lifestyle_score?: number
  school_score?: number
  property_score?: number
  financial_score?: number
  risk_flags?: RiskFlag[]

  executive_summary?: string
  community_narrative?: string
  lifestyle_narrative?: string
  school_narrative?: string
  property_narrative?: string
  financial_narrative?: string

  member_impacts?: MemberImpact[]
  trade_offs?: string[]
  what_to_verify?: string[]
  what_you_may_regret?: string[]
  next_action?: string

  scored_at?: string
  error_message?: string
}

interface RiskFlag {
  type: string
  severity: 'Low' | 'Medium' | 'High' | 'Critical'
  description: string
}

interface MemberImpact {
  member_name: string
  role: string
  summary: string
  positives: string[]
  concerns: string[]
}
```

---

### GET /api/evaluations/family/{family_id}
**Auth required:** Yes

**Response 200:**
```typescript
interface EvaluationListResponse {
  items: EvaluationSummary[]
  total: number
}

interface EvaluationSummary {
  id: string
  property_id: string
  address: string
  family_fit_score?: number
  recommendation?: string
  status: string
  scored_at?: string
}
```

---

### POST /api/properties/{id}/save
Save to shortlist.

**Auth required:** Yes

**Request:** `{}` (empty body)

**Response 200:**
```typescript
interface PropertyActionResponse {
  property_id: string
  status: 'saved'
  preference_events_created: number
}
```

---

### POST /api/properties/{id}/reject
**Auth required:** Yes

**Request:**
```typescript
interface RejectPropertyRequest {
  reason?: string
}
```

**Response 200:** `{ property_id, status: 'rejected' }`

---

### POST /api/properties/{id}/feedback
**Auth required:** Yes

**Request:**
```typescript
interface PropertyFeedbackRequest {
  rating?: 1 | 2 | 3 | 4 | 5
  comment?: string
  member_id?: string   // Which family member is giving feedback
  attribute?: string   // What they're commenting on (e.g. "kitchen", "location")
  sentiment?: 'Positive' | 'Negative' | 'Neutral' | 'Concern' | 'DealBreaker'
}
```

**Response 201:**
```typescript
interface FeedbackResponse {
  id: string
  property_id: string
  preference_event_id: string
  journal_entry_id?: string
}
```

---

### GET /api/suburbs
**Auth required:** Yes

**Response 200:**
```typescript
interface SuburbListResponse {
  items: SuburbSummary[]
}

interface SuburbSummary {
  id: string
  name: string
  postcode: string
  community_score: number
  lifestyle_score: number
  family_density: number
  median_income: number
  distance_to_burleigh_km?: number
}
```

---

### GET /api/suburbs/{id}
**Auth required:** Yes

**Response 200:**
```typescript
interface SuburbDetailResponse {
  id: string
  name: string
  postcode: string
  population: number
  owner_occupier_rate: number
  median_income: number
  crime_index: number
  family_density: number
  community_score: number
  lifestyle_score: number
  metrics: SuburbMetric[]
  schools: SchoolSummary[]
  narrative?: string
  updated_at: string
}

interface SuburbMetric {
  name: string
  value: number | string
  source: string
}
```

---

### GET /api/schools
**Auth required:** Yes

**Query parameters:**
```typescript
{ suburb_id?: string; type?: 'Primary' | 'Secondary' | 'Combined' }
```

**Response 200:**
```typescript
interface SchoolListResponse {
  items: SchoolSummary[]
}

interface SchoolSummary {
  id: string
  name: string
  type: string
  suburb_name: string
  school_score: number
  wellbeing_score: number
  academic_score: number
}
```

---

### GET /api/schools/{id}
**Auth required:** Yes

**Response 200:**
```typescript
interface SchoolDetailResponse {
  id: string
  name: string
  type: string
  suburb_id: string
  suburb_name: string
  school_score: number
  wellbeing_score: number
  academic_score: number
  community_score: number
  commute_score: number
  narrative?: string
  catchment_suburbs: string[]
  updated_at: string
}
```

---

### POST /api/advisor/chat
**Auth required:** Yes | Rate limit: 10/hour

**Request:**
```typescript
interface AdvisorChatRequest {
  message: string
  thread_id?: string    // Omit to start new thread
}
```

**Response 200:**
```typescript
interface AdvisorChatResponse {
  thread_id: string
  reply: string
  preference_signals_detected?: PreferenceSignal[]
  suggested_actions?: SuggestedAction[]
}

interface PreferenceSignal {
  attribute: string
  sentiment: string
  strength: number
  extracted_text: string
}

interface SuggestedAction {
  label: string
  action: string     // e.g. "view_property", "update_preference"
  target_id?: string
}
```

---

### GET /api/advisor/history
**Auth required:** Yes

**Response 200:**
```typescript
interface AdvisorHistoryResponse {
  threads: AdvisorThread[]
}

interface AdvisorThread {
  thread_id: string
  created_at: string
  message_count: number
  last_message_preview: string
  messages: AdvisorMessage[]
}

interface AdvisorMessage {
  role: 'user' | 'assistant'
  content: string
  timestamp: string
}
```

---

### GET /api/journal
**Auth required:** Yes

**Response 200:**
```typescript
interface JournalResponse {
  entries: JournalEntry[]
}

interface JournalEntry {
  id: string
  entry_type: string
  related_property_id?: string
  related_suburb_id?: string
  title: string
  summary: string
  decision?: string
  reasoning?: string
  concerns?: string
  member_impacts?: Record<string, string>
  created_by: string
  created_at: string
}
```

---

### POST /api/journal
**Auth required:** Yes

**Request:**
```typescript
interface CreateJournalEntryRequest {
  entry_type: 'PropertyReview' | 'SuburbReview' | 'SchoolReview' | 'InspectionNote' | 'FamilyDiscussion' | 'Concern'
  title: string
  summary: string
  related_property_id?: string
  related_suburb_id?: string
  related_school_id?: string
  decision?: string
  reasoning?: string
  concerns?: string
  member_impacts?: Record<string, string>
}
```

**Response 201:** `JournalEntry`

---

### GET /api/preferences
**Auth required:** Yes

**Response 200:**
```typescript
interface PreferencesResponse {
  preferences: FamilyPreference[]
  summary: {
    confirmed: number
    emerging: number
    contradicted: number
    retired: number
  }
}

interface FamilyPreference {
  id: string
  attribute: string
  current_weight: number       // 0-5
  confidence: number           // 0.0-1.0
  status: 'Emerging' | 'Confirmed' | 'Contradicted' | 'Retired' | 'Manual'
  positive_signals: number
  negative_signals: number
  member_id?: string
  last_updated: string
}
```

---

### POST /api/inspections
**Auth required:** Yes

**Request:**
```typescript
interface CreateInspectionRequest {
  property_id: string
  inspection_date: string    // ISO 8601
  inspection_time?: string
  agent_name?: string
  agent_phone?: string
  notes?: string
}
```

**Response 201:**
```typescript
interface InspectionResponse {
  id: string
  property_id: string
  property_address: string
  inspection_date: string
  inspection_time?: string
  agent_name?: string
  agent_phone?: string
  notes?: string
  post_inspection_notes?: string
  verdict?: string
  status: 'Scheduled' | 'Completed' | 'Cancelled'
  created_at: string
}
```

---

### PUT /api/inspections/{id}
**Auth required:** Yes

**Request:**
```typescript
interface UpdateInspectionRequest {
  status?: 'Completed' | 'Cancelled'
  post_inspection_notes?: string
  verdict?: 'Inspect Again' | 'Offer' | 'Pass' | 'Reconsider'
  rating?: 1 | 2 | 3 | 4 | 5
}
```

**Response 200:** Updated `InspectionResponse`

---

### GET /api/dashboard
**Auth required:** Yes

**Response 200:**
```typescript
interface DashboardResponse {
  family_name: string
  top_recommendations: PropertyListItem[]    // Up to 5, highest fit score
  recent_activity: ActivityItem[]            // Last 10 events
  shortlist_count: number
  evaluations_count: number
  pending_inspections: InspectionSummary[]
  preference_summary: {
    total_confirmed: number
    emerging_count: number
    learning_confidence: number
  }
}

interface ActivityItem {
  type: 'evaluation_complete' | 'property_saved' | 'property_rejected' | 'inspection_added' | 'journal_entry'
  description: string
  related_id?: string
  related_type?: string
  timestamp: string
}
```

---

## 5. Property Ingestion Pipeline

### Step 1: URL Submission

User pastes a URL from `realestate.com.au` or `domain.com.au`. The frontend validates the format client-side with a regex check before submitting. Backend performs a stricter validation.

```python
# utils/url_validator.py
ALLOWED_DOMAINS = ['realestate.com.au', 'domain.com.au']
PROPERTY_URL_PATTERNS = [
    r'realestate\.com\.au/property-[a-z]+-[a-z\-]+-\d+',
    r'domain\.com\.au/[a-z\-]+-[a-z\-]+-[a-z\-]+-\d+',
]

def validate(url: str) -> None:
    parsed = urlparse(url)
    if not any(domain in parsed.netloc for domain in ALLOWED_DOMAINS):
        raise HTTPException(400, "URL must be from realestate.com.au or domain.com.au")
    if not any(re.search(p, url) for p in PROPERTY_URL_PATTERNS):
        raise HTTPException(400, "URL does not appear to be a property listing")
```

### Step 2: Apify Scrape

Property data is extracted using **Apify** — a managed web scraping platform with purpose-built actors for realestate.com.au and domain.com.au. Apify handles JavaScript rendering, anti-bot protection, and pagination. It returns structured JSON directly, eliminating the need for HTML parsing or AI-based field extraction.

```python
# services/property_ingestion.py
from apify_client import ApifyClient

async def fetch_property_via_apify(url: str) -> dict:
    """
    Submit a listing URL to the appropriate Apify actor.
    Returns structured property JSON.
    """
    client = ApifyClient(settings.APIFY_API_TOKEN)

    # Select actor based on domain
    if "realestate.com.au" in url:
        actor_id = settings.APIFY_REA_ACTOR_ID
    else:
        actor_id = settings.APIFY_DOMAIN_ACTOR_ID

    run_input = {
        "startUrls": [{"url": url}],
        "maxItems": 1,
    }

    # Run actor synchronously (wait for result, typically 10–20 seconds)
    run = client.actor(actor_id).call(run_input=run_input, timeout_secs=60)

    # Fetch result from dataset
    items = list(client.dataset(run["defaultDatasetId"]).iterate_items())
    if not items:
        raise PropertyExtractionError("Apify returned no results for this URL")

    return items[0]  # Structured property dict


def map_apify_to_property(apify_data: dict, url: str) -> ExtractedPropertyData:
    """
    Normalise Apify output to our internal schema.
    Field names vary by actor — normalise here.
    """
    return ExtractedPropertyData(
        address=apify_data.get("address") or apify_data.get("street_address"),
        suburb=apify_data.get("suburb"),
        postcode=apify_data.get("postcode"),
        price_display=apify_data.get("price") or apify_data.get("priceText"),
        bedrooms=apify_data.get("bedrooms"),
        bathrooms=apify_data.get("bathrooms"),
        car_spaces=apify_data.get("carSpaces") or apify_data.get("parking"),
        land_size_sqm=apify_data.get("landArea"),
        house_size_sqm=apify_data.get("buildingArea"),
        property_type=apify_data.get("propertyType", "house"),
        description=apify_data.get("description", ""),
        features=apify_data.get("features", []),
        image_urls=apify_data.get("images", []),
        agent_name=apify_data.get("agentName"),
        agency=apify_data.get("agencyName"),
        listed_date=apify_data.get("listingDate"),
        source_url=url,
        raw_apify_data=apify_data,   # Store original for debugging
    )
```

**Note**: Apify actor field names may differ between REA and Domain actors. The `map_apify_to_property` normalisation layer handles this. Confirm exact field names by testing both actors against real listings before the property ingestion sprint.

### Step 3: AI Qualitative Enrichment (OpenAI)

Apify handles all structured field extraction. OpenAI (GPT-4o-mini) is only called to infer **qualitative attributes** that cannot be extracted structurally:
- Indoor-outdoor flow quality (from description text)
- Modernity assessment (from listing language + listed year if available)
- Design quality estimate (from description keywords: "Hampton's", "coastal contemporary", "architecturally designed")
- Home office suitability (from description if not listed as a feature)

This is a much smaller, cheaper OpenAI call than full extraction, and only runs when the structured Apify data does not already answer the question.

### Step 4: Data Normalisation and Storage

The extracted data is normalised (suburb name → `suburb_id` lookup, price string → integer, etc.) and stored as a `Property` record with `status = 'ingested'`.

### Step 5: Travel Time Fetch (Google Maps)

```python
# services/travel_time.py
BURLEIGH_HEADS = (-28.0853, 153.4565)
BURLEIGH_BEACH = (-28.0744, 153.4573)

async def get_travel_times(property_address: str) -> TravelTimes:
    # Call Google Maps Distance Matrix API
    # Returns drive time in minutes to Burleigh and nearest beach
    # Cache result for 1 hour (traffic is dynamic, property locations are static)
    ...
```

### Step 6: School Catchment Determination

```python
# services/school_catchment.py
async def determine_catchment_schools(suburb_id: str) -> list[School]:
    # Query SchoolCatchments table for this suburb
    # Return all schools that include this suburb in their catchment
    # Cache per suburb for 24h
    ...
```

### Step 7: Scoring Pipeline

```python
# tasks/evaluation_pipeline.py
async def run_evaluation_pipeline(property_id: str, evaluation_id: str, family_id: str):
    async with AsyncSessionLocal() as db:
        try:
            await EvaluationService(db).update_status(evaluation_id, 'processing')

            property = await PropertyRepository(db).get(property_id)
            family = await FamilyRepository(db).get_with_members(family_id)
            memories = await MemoryService(db).get_active_memories(family_id)
            suburb = await get_suburb_with_cache(property.suburb_id)
            schools = await school_catchment_service.determine_catchment_schools(property.suburb_id)
            travel_times = await travel_time_service.get_travel_times(property.address)

            community_result = await CommunityScoringService(db).score(suburb, family)
            lifestyle_result = await LifestyleScoringService(db).score(suburb, travel_times, family)
            school_result = await SchoolScoringService(db).score(schools, travel_times, family)
            property_result = await PropertyScoringService(db).score(property, family)
            financial_result = await FinancialScoringService(db).score(property, suburb, family)
            risk_result = await RiskScoringService(db).score(property, suburb, family)

            family_fit = FamilyFitService.calculate(
                community=community_result.score,
                lifestyle=lifestyle_result.score,
                school=school_result.score,
                property=property_result.score,
                financial=financial_result.score,
            )

            five_year_prediction = await FiveYearPredictionService().predict(
                property, suburb, schools, family, memories, family_fit
            )

            confidence = ConfidenceCalculator.calculate(
                property=property,
                suburb=suburb,
                schools=schools,
                family=family,
                scores=[community_result, lifestyle_result, school_result, property_result]
            )

            recommendation = RecommendationService.determine(family_fit, confidence, risk_result)

            explanation = await ExplainabilityService().generate(
                property, suburb, schools, family, memories,
                community_result, lifestyle_result, school_result,
                property_result, financial_result, risk_result,
                family_fit, five_year_prediction, confidence, recommendation
            )

            await EvaluationRepository(db).save_complete(evaluation_id, EvaluationData(
                family_fit_score=family_fit,
                five_year_fit_score=five_year_prediction.score,
                confidence_score=confidence.score,
                confidence_label=confidence.label,
                recommendation=recommendation,
                **explanation.to_dict()
            ))

            await MemoryService(db).update_from_evaluation(family_id, property, explanation)
            await DecisionJournalService(db).create_from_evaluation(family_id, property, explanation)
            await PreferenceLearningService(db).update_from_evaluation(family_id, property, explanation)

        except Exception as e:
            await EvaluationService(db).update_status(evaluation_id, 'failed', str(e))
            logger.error(f"Evaluation pipeline failed for {evaluation_id}: {e}")
```

### Step 8: Frontend Polling

Frontend polls `GET /api/evaluations/{id}` every 3 seconds until `status = 'complete'` or `status = 'failed'`. A loading state shows the pipeline progress (ingested → scoring → complete). On completion, the evaluation panel renders with all scores and narratives.

---

## 6. Infrastructure and Deployment

### 6.1 Vercel (Frontend)

```javascript
// next.config.js
/** @type {import('next').NextConfig} */
const nextConfig = {
  images: {
    domains: ['res.cloudinary.com', 'images.domain.com.au', 'bucket.realestate.com.au'],
  },
  async rewrites() {
    // No rewrites needed — Next.js API routes handle backend forwarding
    return []
  },
  // ISR for suburb pages
  experimental: {
    incrementalCacheHandlerPath: undefined,
  },
}
module.exports = nextConfig
```

Suburb pages (`/suburbs/[id]`) use ISR with a 24-hour revalidation period. All user-specific pages (dashboard, properties, advisor) are server-rendered with Clerk session.

### 6.2 Railway Services

Three Railway services in one project:
1. **PostgreSQL** — managed Railway postgres, 1GB storage for MVP
2. **Redis** — managed Railway Redis, 256MB for MVP
3. **FastAPI** — Dockerfile-based deployment, 2 replicas in production

```dockerfile
# Dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2"]
```

### 6.3 Environment Separation

| Environment | Frontend | Backend | Database |
|---|---|---|---|
| Development | `localhost:3000` | `localhost:8000` | Local PostgreSQL |
| Staging | `gcmove-staging.vercel.app` | `gcmove-api-staging.railway.app` | Railway staging DB |
| Production | `gcmove.vercel.app` | `gcmove-api.railway.app` | Railway prod DB |

### 6.4 CI/CD (GitHub Actions)

```yaml
# .github/workflows/deploy.yml
name: Deploy

on:
  push:
    branches: [main]

jobs:
  test-backend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v4
        with: { python-version: '3.11' }
      - run: pip install -r requirements.txt -r requirements-dev.txt
      - run: pytest tests/ -v --cov=. --cov-report=xml

  test-frontend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with: { node-version: '20' }
      - run: npm ci
      - run: npm run type-check
      - run: npm run lint

  deploy-backend:
    needs: [test-backend]
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: bervProject/railway-deploy@v1
        with:
          railway_token: ${{ secrets.RAILWAY_TOKEN }}
          service: gcmove-api

  # Vercel deploys automatically on push to main via Vercel GitHub integration
```

### 6.5 Database Migrations (Alembic)

```bash
# Generate migration
alembic revision --autogenerate -m "add_five_year_score_to_evaluations"

# Apply migrations (run in CI before deploy, or as Railway deploy command)
alembic upgrade head
```

Railway deploy command: `alembic upgrade head && uvicorn main:app --host 0.0.0.0 --port 8000`

---

## 7. Security

### 7.1 Authentication Flow

1. User authenticates with Clerk (email/password or social)
2. Clerk issues a signed JWT (RS256)
3. Next.js reads JWT from Clerk session cookie server-side
4. Next.js API routes attach JWT as `Authorization: Bearer` header before calling FastAPI
5. FastAPI middleware verifies JWT signature against Clerk JWKS endpoint (cached)
6. `clerk_user_id` extracted from JWT `sub` claim
7. Family record looked up by `clerk_user_id`
8. All subsequent queries scoped to `family_id`

### 7.2 Data Isolation

Every database query that returns user data MUST include `WHERE family_id = :family_id`. This is enforced at the repository layer, not the router layer. Repositories accept `family_id` as a required parameter.

```python
# Correct
async def get_properties(db: AsyncSession, family_id: str) -> list[Property]:
    result = await db.execute(
        select(Property).where(Property.family_id == family_id)
    )
    return result.scalars().all()

# Never do this
async def get_properties(db: AsyncSession) -> list[Property]:  # Missing family_id
    ...
```

### 7.3 Rate Limiting on AI Endpoints

```python
# Sliding window rate limit via Redis
# /api/advisor/chat: 10 requests per hour per family_id
# /api/properties/ingest: 20 per day per family_id
# /api/evaluations: 20 per day per family_id
```

### 7.4 URL Validation

Only `realestate.com.au` and `domain.com.au` URLs are accepted for property ingestion. URL is validated against both domain and URL structure patterns before any HTTP request is made.

---

## 8. Performance

### 8.1 Caching Strategy

| Data | Cache Duration | Reason |
|---|---|---|
| Suburb data | 24 hours | Rarely changes |
| School data | 24 hours | Static |
| Travel times | 1 hour | Traffic changes |
| AI-generated suburb narratives | 7 days | Expensive, stable |
| Property extraction | Never | Listing data changes |
| Family data | No cache | Must be fresh |

### 8.2 Database Indexes

```sql
-- Critical indexes (Alembic migration)
CREATE INDEX idx_properties_family_id ON properties(family_id);
CREATE INDEX idx_evaluations_family_id ON evaluations(family_id);
CREATE INDEX idx_evaluations_property_id ON evaluations(property_id);
CREATE INDEX idx_evaluations_status ON evaluations(status);
CREATE INDEX idx_preference_events_family_id ON preference_events(family_id);
CREATE INDEX idx_family_memory_family_id ON family_memory(family_id);
CREATE INDEX idx_journal_entries_family_id ON journal_entries(family_id);
CREATE INDEX idx_school_catchments_suburb_id ON school_catchments(suburb_id);
```

### 8.3 Frontend Performance

Suburb detail pages use ISR (revalidate every 24 hours). Property list uses cursor-based pagination, not offset-based. Images served via Cloudinary with automatic format and size optimisation. React Query handles deduplication of concurrent requests automatically.

### 8.4 Optimistic UI

Property save/reject/feedback actions update the local React Query cache immediately before the server confirms. On error, the cache is rolled back. This gives instant perceived performance on the most frequent user interactions.

---

## 9. Monitoring

### 9.1 Sentry Configuration

```typescript
// sentry.client.config.ts
import * as Sentry from "@sentry/nextjs"
Sentry.init({
  dsn: process.env.NEXT_PUBLIC_SENTRY_DSN,
  tracesSampleRate: 0.1,
  environment: process.env.NODE_ENV,
})
```

```python
# main.py (FastAPI)
import sentry_sdk
sentry_sdk.init(
    dsn=settings.SENTRY_DSN,
    traces_sample_rate=0.1,
    profiles_sample_rate=0.1,
)
```

Key Sentry alerts: evaluation pipeline failures, OpenAI API errors, JWT verification failures, database connection errors.

### 9.2 PostHog Event Tracking Plan

| Event | When Triggered | Properties |
|---|---|---|
| `property_url_submitted` | User submits URL | `url_domain`, `family_id` |
| `evaluation_completed` | Evaluation finishes | `recommendation`, `family_fit_score`, `duration_ms` |
| `property_saved` | User saves to shortlist | `property_id`, `family_fit_score` |
| `property_rejected` | User rejects property | `property_id`, `reason` |
| `advisor_message_sent` | Chat message sent | `thread_id`, `message_length` |
| `inspection_created` | Inspection logged | `property_id`, `days_until_inspection` |
| `journal_entry_created` | Journal entry added | `entry_type` |
| `shortlist_viewed` | Shortlist opened | `shortlist_count` |
| `profile_completed` | All family members added | `member_count` |

### 9.3 Health Check Endpoints

```python
@app.get("/health")
async def health_check():
    return {"status": "ok", "version": "1.0.0", "timestamp": datetime.utcnow().isoformat()}

@app.get("/health/deep")
async def deep_health_check(db: AsyncSession = Depends(get_db)):
    # Check DB connection
    await db.execute(text("SELECT 1"))
    # Check Redis
    await redis.ping()
    return {"status": "ok", "db": "ok", "redis": "ok"}
```

---

*Document complete. Proceed to AI Architecture document for intelligence layer specification.*
