# GC Move OS — Data Architecture
**Document 5 of 6 | Classification: Internal Engineering | Version 1.0 | June 2026**

---

## 1. Data Architecture Overview

### 1.1 Data Domains

Gold Coast Move OS organises data into five distinct domains. Each domain has a clear ownership boundary and interacts with others through well-defined interfaces.

```
┌──────────────────────────────────────────────────────────────────────┐
│                        FAMILY DOMAIN                                 │
│  Family | FamilyMember | FamilyPreferences | FamilyMemory            │
│  PreferenceEvents | MemoryEvents | DecisionJournal                   │
└─────────────────────────┬────────────────────────────────────────────┘
                          │ references
          ┌───────────────┼────────────────────┐
          ▼               ▼                    ▼
┌─────────────────┐ ┌───────────────┐ ┌──────────────────┐
│ PROPERTY DOMAIN │ │ LOCATION      │ │ INTELLIGENCE     │
│ Property        │ │ DOMAIN        │ │ DOMAIN           │
│ PropertyFeatures│ │ Suburb        │ │ PropertyEvaluation│
│ PropertyImages  │ │ SuburbMetrics │ │ EvaluationScores │
│ PropertyHistory │ │ LifestyleAssets│ │ Recommendations  │
│ Inspections     │ │ School        │ │ AIAdvisorThreads  │
└────────┬────────┘ │ SchoolCatchm. │ └──────────────────┘
         │          └───────────────┘
         │
┌────────▼────────┐
│ OPERATIONAL     │
│ DOMAIN          │
│ AuditLog        │
│ Notifications   │
│ MarketSnapshot  │
└─────────────────┘
```

### 1.2 Data Flow Architecture

The system has three primary data flow patterns:

**Pattern A — Property Ingestion (User-Initiated)**
```
User pastes URL
  → FastAPI ingestion endpoint
  → OpenAI extraction (GPT-4o) — extracts price, bedrooms, features, description
  → Validation layer (required fields, data quality scoring)
  → INSERT into properties + property_features + property_images
  → Trigger suburb lookup (does suburb already exist in suburbs table?)
    → If yes: attach suburb_id to property
    → If no: flag for admin seeding (MVP: suburb must be pre-seeded)
  → Trigger async evaluation job (Celery / background task)
  → Return property_id to frontend
```

**Pattern B — Evaluation Pipeline (Background, Async)**
```
PropertyID enqueued
  → Load property + features
  → Load suburb_metrics + lifestyle_assets for suburb
  → Load school data for catchment suburbs
  → Load family preferences + memory
  → OpenAI scoring prompt (structured JSON output)
  → INSERT property_evaluations record
  → INSERT evaluation_scores record
  → INSERT recommendation record
  → Cache evaluation result in Redis (key: eval:{family_id}:{property_id})
  → Emit WebSocket notification to frontend
```

**Pattern C — Preference Learning (Continuous)**
```
User action (save, reject, rate, comment, inspect)
  → INSERT preference_event
  → Async preference aggregation job
  → Load all preference_events for family by attribute
  → Recalculate current_weight + confidence for attribute
  → UPSERT family_preferences record
  → Invalidate affected cached evaluations
  → INSERT memory_event audit record
```

### 1.3 Read vs Write Patterns

| Operation | Pattern | Frequency | Optimisation |
|---|---|---|---|
| Load property list with scores | Read-heavy | Many times/session | Materialised view + Redis cache |
| Load suburb scores | Read-heavy | Dozens/session | Redis cache, 24h TTL |
| Submit preference event | Write | Every user action | Async, fire-and-forget |
| Run property evaluation | Write-heavy | Once per property | Background job |
| Load family memory | Read | On every AI advisor call | Redis, 1h TTL |
| Decision journal read | Read | Occasional | No cache needed |
| Audit log writes | Write-only | Every action | Async, append-only table |

### 1.4 Caching Strategy Summary

Redis is the sole caching layer. PostgreSQL is the source of truth. No in-memory caching in FastAPI processes (stateless, horizontally scalable on Railway).

Cache namespaces:
- `suburb:{suburb_id}:scores` — suburb scoring composite
- `suburb:{suburb_id}:lifestyle` — POI counts and distances
- `school:{school_id}:metrics` — school scoring composite
- `eval:{family_id}:{property_id}` — full evaluation result
- `family:{family_id}:preferences` — learned preference weights
- `family:{family_id}:memory:{type}` — memory by type
- `travel:{origin_hash}:{destination_slug}` — Google Maps travel times

---

## 2. External Data Sources

### 2.1 ABS Census — Suburb Demographics

**Source**: Australian Bureau of Statistics  
**URL**: https://www.abs.gov.au/census/find-census-data/datapacks  
**Data product**: General Community Profile (GCP) DataPacks, 2021 Census  

**Data type**: CSV/XLSX bulk download, structured tabular  
**Fields used**:
- `B18` table: Dwelling structure (owner occupier rate calculation)
- `B06`: Age by sex (family density — children 0–14 per household)
- `B15`: Type of educational institution attending (educational attainment proxy)
- `B33`: Total personal income (median household income)
- `B02`: Selected medians and averages (median weekly household income)

**Update frequency**: Census is published every 5 years. Next release: 2026. Use 2021 DataPack until 2026 data is available.  
**Integration method**: Manual bulk download, transform via Python ETL script, seed into `suburb_metrics` table.  
**Licensing**: Creative Commons Attribution 4.0. Free to use, attribution required in product.  
**Fallback**: If ABS data is unavailable for a suburb, `community_score` is calculated from available sub-scores only, with `confidence_score` reduced by 0.15 per missing metric.

**Pre-seeding action**: Download 2021 GCP DataPack for Queensland Statistical Area 2 (SA2). Filter to Gold Coast SA2s matching target suburb list. Run seeding script before launch.

---

### 2.2 QLD Police Crime Statistics

**Source**: Queensland Police Service  
**URL**: https://www.police.qld.gov.au/maps-and-statistics  
**Data product**: Queensland Crime Statistics — Offences by Division/District downloadable CSV  

**Data type**: CSV, quarterly release  
**Fields used**:
- Division name (maps to suburb or police division)
- Offence category: property offences, personal offences, drug offences
- Count per division per quarter
- Rate per 100,000 population

**Update frequency**: Quarterly. Refresh ETL runs quarterly via scheduled job.  
**Integration method**: Download from QPS statistics portal (no public API). Transformation script normalises division names to suburb names using a maintained mapping table. Crime index calculated as weighted composite of property + personal offence rates normalised to Gold Coast average.  
**Licensing**: Open data under Queensland Government Information Licensing Framework. Free use.  
**Fallback**: If no crime data maps to a suburb, use parent LGA (Gold Coast City Council) average rate. Flag `crime_index_source = 'lga_average'` in `suburb_metrics`.

**Note**: QPS divisions do not map 1:1 to suburbs. A maintained `suburb_to_police_division` lookup table in the database handles this mapping.

---

### 2.3 ACARA MySchool — School Performance Data

**Source**: Australian Curriculum, Assessment and Reporting Authority  
**URL**: https://www.myschool.edu.au  
**Data product**: MySchool public data (downloadable datasets page) — NAPLAN results, school profile  

**Data type**: CSV bulk download (ACARA releases annual school data files)  
**Fields used**:
- ACARA School ID (primary key for matching)
- School name, sector (government / Catholic / independent)
- Year range offered
- Total enrolments
- NAPLAN proficiency percentages: Reading, Writing, Numeracy (Years 3, 5, 7, 9)
- Index of Community Socio-Educational Advantage (ICSEA)
- Student attendance rate

**Update frequency**: Annually (typically released mid-year for prior academic year).  
**Integration method**: Manual download from ACARA Data Access Program. Python ETL maps ACARA School ID to `schools.acara_school_id`. Academic outcomes sub-score calculated from NAPLAN proficiency bands relative to state average.  
**Licensing**: Creative Commons Attribution. Free to use.  
**Fallback**: If NAPLAN data is missing (e.g., small school cohort suppressed), academic outcome sub-score uses ICSEA as a proxy with `confidence_score` reduced by 0.10.

**Additional source**: School websites / prospectus documents for extracurricular programs, pathway data, wellbeing programs. These are ingested via OpenAI extraction (same pipeline as property ingestion) and stored in `school_metrics`.

---

### 2.4 Google Maps Platform — Travel Times and POI Counts

**Source**: Google Maps Platform  
**URL**: https://developers.google.com/maps  
**APIs used**:
- Distance Matrix API (travel times)
- Places API (Nearby Search for lifestyle POI counts)

**Data type**: JSON REST API  
**Fields used from Distance Matrix**:
- `duration.value` (seconds) — drive time from property/suburb centroid to Burleigh Heads centre, Broadbeach, beach access points, key schools
- `distance.value` (metres)

**Fields used from Places API**:
- Place type counts per suburb bounding box: `cafe`, `gym`, `spa`, `park`, `restaurant`, `shopping_mall`, `yoga_studio`
- Used to calculate `cafe_dining_score`, `wellness_infrastructure_score`

**Update frequency**: Travel times are cached for 30 days per origin-destination pair. POI counts refreshed monthly.  
**Integration method**: Direct API call from FastAPI service. Results cached in Redis and persisted to `suburb_lifestyle_assets` table.  
**Licensing/cost**: Pay-per-use. Distance Matrix: AUD $0.01 per element. Places Nearby: AUD $0.04 per request. Budget ~$50/month at MVP scale. Requires billing account and API key with appropriate restrictions.  
**Fallback**: If Google Maps API is unavailable, use cached values from `suburb_lifestyle_assets`. If no cached values, travel time is estimated from straight-line distance × 1.4 factor. Flag `travel_time_source = 'estimated'`.

---

### 2.5 OpenStreetMap / Overpass API — Lifestyle POI Data

**Source**: OpenStreetMap via Overpass API  
**URL**: https://overpass-api.de  
**Purpose**: Free alternative/supplement to Google Places for POI counts  

**Data type**: JSON via Overpass QL queries  
**Fields used**:
- `amenity=cafe`, `amenity=restaurant`, `leisure=fitness_centre`, `leisure=park`, `shop=organic`, `leisure=swimming_pool`
- Node/way coordinates within suburb polygon

**Update frequency**: OSM is community-edited, refreshed monthly via scheduled Overpass query.  
**Integration method**: Overpass QL query scoped to suburb bounding box polygon. Python parser counts features by type. Results stored in `suburb_lifestyle_assets.osm_poi_counts` (JSONB column).  
**Licensing**: ODbL (Open Database Licence). Free to use. Attribution required.  
**Fallback**: Use Google Places counts if OSM query fails. OSM is used primarily to cross-validate Google data and provide POI counts for categories not well-covered by Google Places.

---

### 2.6 Queensland Government Flood Maps

**Source**: Queensland Government — Queensland Reconstruction Authority  
**URL**: https://www.qldfloodcheck.com.au / https://www.data.qld.gov.au  
**Data product**: Queensland Flood Information Portal, QFlood dataset  

**Data type**: REST API (GeoJSON) and downloadable shapefiles  
**Fields used**:
- Flood modelled area (1-in-100 year ARI)
- Flood depth at address (where available)
- Flood zone classification: high / medium / low / no-risk

**Update frequency**: Updated by QRA after major flood events. Refresh annually or after declared flood events.  
**Integration method**: API call using property address coordinates (lat/lng) against QFlood GeoJSON layer. Result stored as `flood_risk_category` (enum: high/medium/low/none) and `flood_risk_source_date` in `properties` table.  
**Licensing**: Creative Commons Attribution 4.0 — Queensland Government. Free.  
**Fallback**: If API is unavailable, flag `flood_risk_category = 'unknown'`. This reduces `confidence_score` by 0.10 and triggers a UI warning to user.

---

### 2.7 REA / Domain Listing Pages — Property Ingestion

**Source**: realestate.com.au, domain.com.au listing pages  
**Purpose**: Primary property data ingestion channel at MVP  

**Data type**: HTML web pages (user-pasted URLs)  
**Integration method**: User pastes listing URL → FastAPI calls OpenAI GPT-4o with the URL (via web browsing capability) or with page HTML (fetched by backend) → Structured extraction prompt returns JSON with standardised fields.  

**Extraction target fields**:
- `listing_price` or `price_range_low` / `price_range_high`
- `address_street`, `address_suburb`, `address_state`, `address_postcode`
- `bedrooms`, `bathrooms`, `car_spaces`
- `land_area_sqm`, `house_area_sqm`
- `property_type` (house/townhouse/unit)
- `pool` (boolean), `solar` (boolean), `air_conditioning` (boolean)
- `description_text` (full listing description)
- `agent_name`, `agency_name`
- `listing_id` (REA/Domain ID from URL)
- Image URLs (first 10)

**Update frequency**: Ingested once per listing URL. Property status re-checked weekly via re-fetch (sold detection).  
**Licensing**: No formal API access at MVP. Ingestion is user-initiated (user pastes their own viewed URL). Phase 2 evaluates REA Group data partnership or PropTrack API.  
**Fallback**: If OpenAI extraction fails or returns low-confidence fields, flag individual fields with `extracted_confidence < 0.7` and prompt user to manually confirm those fields in the UI.

---

### 2.8 PropTrack API — Market Data (Phase 2)

**Source**: PropTrack (REA Group subsidiary)  
**URL**: https://www.proptrack.com.au/proptrack-api  
**Purpose**: Automated property valuation, sales history, suburb market trends  

**Data type**: JSON REST API  
**Fields used** (Phase 2):
- Automated valuation estimate (AVM) + confidence range
- Days on market
- Comparable sales (last 6 months)
- Suburb median price (house, unit)
- Suburb price growth (1yr, 3yr, 5yr)
- Rental yield estimates

**Update frequency**: Real-time (AVM), daily (market data).  
**Integration method**: Direct API integration with PropTrack credentials. Results stored in `market_snapshot` table.  
**Licensing/cost**: Commercial API licence required. Contact PropTrack for pricing. Estimated AUD $500–2,000/month depending on volume.  
**Phase 2 trigger**: Integrate when family user base exceeds 50 active families or when financial scoring module is built.  
**Fallback at MVP**: Financial score uses listing price only (no AVM). Market growth data sourced manually from REIQ quarterly reports and seeded into `suburb_metrics`.

---

## 3. Data Pipeline Architecture

### 3.1 Property Ingestion Pipeline

```
STEP 1 — URL Receipt
  Input: listing_url (string), family_id (UUID)
  Action: Validate URL format (must be realestate.com.au or domain.com.au)
  Output: URL accepted, job_id issued

STEP 2 — Page Fetch
  Input: listing_url
  Action: FastAPI backend fetches page HTML (requests + BeautifulSoup)
          OR OpenAI web browsing if HTML fetch is blocked
  Output: raw_html or page_text

STEP 3 — OpenAI Extraction
  Input: raw_html / page_text + extraction system prompt
  Action: GPT-4o call with structured JSON output schema
  Temperature: 0.0 (deterministic extraction)
  Output: PropertyExtraction JSON object with confidence per field

STEP 4 — Validation
  Input: PropertyExtraction JSON
  Rules:
    - address_suburb must exist in suburbs table (reject if not pre-seeded)
    - listing_price must be numeric > 0
    - bedrooms must be integer 1–10
    - property_type must be in enum
  Output: ValidationResult (passed/failed fields, data_quality_score 0–100)

STEP 5 — Deduplication Check
  Input: address_street + address_postcode
  Action: Check properties table for existing record with same address
  If duplicate: return existing property_id with `is_duplicate = true`
  Output: is_new_property boolean

STEP 6 — Database Write
  Tables written:
    - properties (core record)
    - property_features (key-value rows from extracted features)
    - property_images (first 10 image URLs)
  Output: property_id (UUID)

STEP 7 — Flood Risk Enrichment (async)
  Input: property lat/lng (geocoded from address)
  Action: Call QFlood API
  Output: UPDATE properties SET flood_risk_category = ...

STEP 8 — Evaluation Trigger
  Action: Enqueue property_id + family_id into evaluation job queue (Redis queue)
  Output: evaluation job queued
```

### 3.2 Suburb Data Refresh Pipeline

Runs: Quarterly (ABS/crime) and Monthly (POI counts, travel times)

```
STEP 1 — Trigger: Scheduled job (Railway Cron)

STEP 2 — For each suburb in suburbs table:
  a. Fetch OSM POI counts via Overpass API
  b. Fetch Google Places counts (if budget allows)
  c. Fetch travel times to key destinations (Burleigh Heads, beach, airport)
     — Origin: suburb centroid lat/lng
     — Destinations: hardcoded list of Gold Coast destinations
  d. UPDATE suburb_lifestyle_assets with new counts
  e. UPDATE suburb_metrics with refreshed ABS/crime data (if quarterly)
  f. Recalculate suburb_scores composite
  g. Invalidate Redis cache: suburb:{suburb_id}:*

STEP 3 — Log completion to audit_log
```

### 3.3 School Data Refresh Pipeline

Runs: Annually (January, after ACARA data release)

```
STEP 1 — Download ACARA school data CSV
STEP 2 — Match on acara_school_id to schools table
STEP 3 — UPDATE school_metrics (NAPLAN scores, ICSEA, enrolments)
STEP 4 — Recalculate school academic_outcomes_score
STEP 5 — Invalidate Redis cache: school:{school_id}:*
STEP 6 — Re-evaluate all properties that reference affected school catchments
         (enqueue re-evaluation jobs for all property_evaluations with school_id)
```

### 3.4 Preference Learning Pipeline

Runs: After every PreferenceEvent INSERT (async, background task)

```
STEP 1 — New preference_event inserted for family_id + attribute

STEP 2 — Load all preference_events for this family + attribute (last 90 days)

STEP 3 — Calculate aggregate signals:
  positive_count = COUNT WHERE sentiment IN ('Positive')
  negative_count = COUNT WHERE sentiment IN ('Negative', 'DealBreaker')
  weighted_sum = SUM(strength × sentiment_direction × source_weight)
    where source_weight:
      UserStated = 1.0
      InspectionNote = 0.9
      UserRating = 0.8
      SavedProperty = 0.6
      RejectedProperty = 0.6
      Comment = 0.5
      AIInferred = 0.3
      ManualOverride = 1.0 (overrides all)

STEP 4 — Derive new current_weight (0–5):
  raw_weight = weighted_sum / total_interactions
  current_weight = clamp(raw_weight × 5, 0, 5)

STEP 5 — Calculate confidence (0.0–1.0):
  confidence = min(1.0, total_interactions / 10) × consistency_factor
  consistency_factor = 1 - (contradictions / total_interactions)

STEP 6 — Determine status:
  ManualOverride exists → status = 'Manual'
  confidence > 0.7 AND consistent → status = 'Confirmed'
  confidence 0.3–0.7 → status = 'Emerging'
  contradictions > 50% → status = 'Contradicted'

STEP 7 — UPSERT family_preferences record

STEP 8 — INSERT memory_event (type=Preference, attribute, old_weight, new_weight)

STEP 9 — Invalidate Redis cache: family:{family_id}:preferences
```

### 3.5 Memory Consolidation Pipeline

Runs: Daily at 03:00 AEST (Railway Cron)

```
STEP 1 — Load all families with activity in last 24 hours

STEP 2 — For each family:
  a. Review Session memories older than 24 hours → archive or promote to Learned
  b. Review Learned memories with declining confidence → flag for review
  c. Identify contradicting preference signals → INSERT memory_event (type=Contradiction)
  d. Promote high-confidence Learned memories → Permanent (if confidence > 0.85 for 30+ days)
  e. Retire preferences not signalled in 60+ days → status = 'Retired'

STEP 3 — Summarise family memory state via OpenAI
  (generates a natural-language summary of what the system has learned about this family)
  Stored in family_memory WHERE type = 'Learned' AND attribute = 'family_summary'

STEP 4 — Log consolidation event to audit_log
```

### 3.6 Daily Recommendation Pipeline

Runs: Daily at 06:00 AEST (Railway Cron)

```
STEP 1 — Load all active families

STEP 2 — For each family:
  a. Load all saved/active properties (status NOT IN 'rejected', 'sold')
  b. Check if any property evaluation is stale (last_evaluated > 7 days)
     → Enqueue re-evaluation if family preferences have changed since last eval
  c. Load current family_preferences (current weights)
  d. Recalculate family_fit_score for each property using current weights
  e. Update recommendations table (position, score delta, status change)
  f. Identify any status changes (new #1, dropped from top 3)
  g. INSERT notification if ranking change is significant (>10 points)

STEP 3 — Generate daily digest summary via OpenAI
  (personalised insight: "Robina Heights has moved up because your inspection notes
   confirmed pool is a priority")

STEP 4 — Update Redis cache for affected evaluations
```

---

## 4. Caching Strategy

### 4.1 What Is Cached and TTL

| Cache Key Pattern | Content | TTL | Invalidation Trigger |
|---|---|---|---|
| `suburb:{id}:scores` | Composite suburb scores | 24 hours | Suburb data refresh job |
| `suburb:{id}:lifestyle` | POI counts, travel times | 24 hours | Monthly refresh job |
| `school:{id}:metrics` | School scores composite | 7 days | Annual school data refresh |
| `eval:{family_id}:{property_id}` | Full evaluation JSON | 1 hour | New preference event for family |
| `family:{family_id}:preferences` | Preference weights dict | 1 hour | New preference event |
| `family:{family_id}:memory:permanent` | Permanent memories | 4 hours | Memory consolidation |
| `family:{family_id}:memory:learned` | Learned memories | 1 hour | Preference learning pipeline |
| `travel:{hash}:{dest}` | Travel time in minutes | 30 days | Manual invalidation only |
| `property:{id}:summary` | AI-generated property summary | 6 hours | Property data update |

### 4.2 Redis Key Naming Convention

Keys follow the pattern: `{namespace}:{entity_id}:{sub-key}`

All keys must include a version prefix when schema changes: `v1:suburb:{id}:scores`

Keys are stored as JSON strings (not Redis hashes) for simplicity at MVP scale.

Key compression: suburb and school data compressed with zlib before storage (large JSONB payloads). Property evaluations stored as plain JSON (< 10KB per record).

### 4.3 Cache Warming

On application start (Railway deployment):
1. Warm all `suburb:{id}:scores` keys for 16 target suburbs
2. Warm all `school:{id}:metrics` keys for seeded schools
3. Do NOT warm family-specific caches (populated on first request)

Cache warming is implemented as a FastAPI startup event handler.

### 4.4 Cache Invalidation Triggers

| Event | Keys Invalidated |
|---|---|
| New preference_event inserted | `eval:{family_id}:*`, `family:{family_id}:preferences`, `family:{family_id}:memory:*` |
| Suburb data refresh | `suburb:{suburb_id}:*` |
| School data refresh | `school:{school_id}:*` |
| Property evaluation complete | `eval:{family_id}:{property_id}` |
| Memory consolidation | `family:{family_id}:memory:*` |

Pattern-based invalidation uses Redis `SCAN` + `DEL` (not `KEYS` — production safe).

---

## 5. Data Quality and Validation

### 5.1 Required vs Optional Fields

**Properties — Required (reject ingestion if missing)**:
- `address_street`, `address_suburb`, `address_postcode`
- `listing_price` (or price range low)
- `bedrooms`, `bathrooms`
- `property_type`

**Properties — Optional (reduce confidence score if missing)**:
- `land_area_sqm` (−0.05 confidence)
- `house_area_sqm` (−0.05 confidence)
- `description_text` (−0.10 confidence — limits AI analysis quality)
- `car_spaces` (−0.02 confidence)
- All feature flags (pool, solar, AC) default to `null`, not `false`

### 5.2 Validation Rules

| Field | Rule | Error Handling |
|---|---|---|
| `address_suburb` | Must match `suburbs.name` exactly (case-insensitive) | Reject + prompt user |
| `listing_price` | Must be > 500,000 and < 20,000,000 (Gold Coast range) | Warn + ask user to confirm |
| `bedrooms` | Integer 1–10 | Reject if outside range |
| `land_area_sqm` | Must be > 0 and < 50,000 | Warn if > 5,000 (unusual) |
| `property_type` | Must be in enum: house, townhouse, unit, acreage | Default to 'house' with flag |
| Image URLs | Must be valid HTTPS URLs | Skip invalid, log warning |
| `flood_risk_category` | Enum: high, medium, low, none, unknown | Default unknown |

### 5.3 Data Quality Score

Each property record has a `data_quality_score` (0–100):

```
Base score: 100

Deductions:
  - No description_text: −20
  - No land_area_sqm: −10
  - No house_area_sqm: −10
  - No images: −10
  - Price is a range (not exact): −5
  - Flood risk unknown: −5
  - No agent information: −5
  - No car spaces: −5

Quality tiers:
  80–100: High quality — full AI analysis possible
  60–79: Medium quality — analysis with caveats
  40–59: Low quality — limited analysis, prompt user to add details
  <40: Poor quality — evaluation blocked until data improved
```

### 5.4 Confidence Score Propagation

The `confidence_score` on `evaluation_scores` (0.0–1.0) is the product of:
- Base AI confidence (from GPT-4o response)
- Data quality factor: `data_quality_score / 100 × 0.3 + 0.7` (quality can reduce max confidence to 0.7)
- Suburb data completeness factor
- School data availability factor
- Number of family preference events (more events = higher confidence in fit scores)

Formula:
```
confidence = ai_confidence × data_quality_factor × suburb_completeness × school_completeness × preference_maturity_factor
```

`preference_maturity_factor` = min(1.0, total_family_preference_events / 50)

---

## 6. Data Retention and Privacy

### 6.1 Retention Policy

| Data Type | Retention Period | Reason |
|---|---|---|
| Family account data | Until account deletion + 90 days | Account recovery window |
| Property evaluations | 2 years | Decision audit trail |
| Preference events | 2 years | Preference learning model |
| Memory events | 2 years | Audit trail |
| Decision journal | Indefinite (user-owned) | User's personal record |
| AI advisor messages | 12 months | Conversation history |
| Audit logs | 7 years | Compliance (financial advice adjacent) |
| Soft-deleted records | 90 days, then hard delete via cron | GDPR/Privacy Act compliance |
| Property images (URLs) | Until property is hard-deleted | No binary storage (URLs only) |
| Session memories | 24 hours | Transient by definition |

### 6.2 Personal Data Classification

| Data | Classification | Handling |
|---|---|---|
| Family member names | Personal | Never logged in plain text in audit logs |
| Children's names/ages | Sensitive | Access restricted to family's own records (RLS) |
| Family preferences | Personal | Not shared across families, not used for training |
| AI conversation history | Personal | Stored encrypted at rest (Railway disk encryption) |
| Email (via Clerk) | Personal | Stored only in Clerk, not in our PostgreSQL |
| Property addresses viewed | Personal | Retained per retention policy |

### 6.3 Soft Delete Policy

All tables with user data use `deleted_at TIMESTAMPTZ`. Hard deletes never occur in application code.

Hard delete cron runs weekly:
```sql
DELETE FROM table WHERE deleted_at < NOW() - INTERVAL '90 days';
```

Cascade soft delete: when a family is soft-deleted, all child records (properties, evaluations, preferences, memories, journal entries) are soft-deleted in the same transaction.

### 6.4 Australian Privacy Act Compliance

Key obligations under the Privacy Act 1988 (Cth) and Australian Privacy Principles (APPs):

- **APP 1 (Open and transparent management)**: Privacy policy must be published at `/privacy`. Data architecture must be documented and available to users on request.
- **APP 3 (Collection of solicited personal information)**: Collect only what is needed. Do not collect health information about family members beyond age/life stage.
- **APP 6 (Use or disclosure)**: Family data used only to provide the service. Not shared with third parties (including REA/Domain) without consent.
- **APP 11 (Security of personal information)**: Encrypt data in transit (TLS 1.2+) and at rest. Railway provides encryption at rest. Database password and API keys in environment variables, not code.
- **APP 12 (Access to personal information)**: Users can export all their data via `/api/family/export` endpoint (Phase 2 feature).
- **APP 13 (Correction of personal information)**: Users can delete preferences and journal entries via UI.
- **Notifiable Data Breaches**: If a breach occurs involving personal information, notify OAIC and affected individuals within 30 days.

**Note**: This product provides decision support, not licensed financial advice. Ensure product copy and terms are clear that recommendations are informational only.

---

## 7. Pre-seeding Requirements

All of the following must be present in the database before the application can function for the first family user.

### 7.1 Gold Coast Suburb Reference Data

The following 16 suburbs must be seeded with:
- Name, postcode, lat/lng centroid
- Tier classification (A/B/C)
- Initial suburb_metrics (ABS Census 2021 data)
- Initial lifestyle_assets (OSM/Google POI counts)
- Travel times to Burleigh Heads CBD

| Suburb | Postcode | Tier | Notes |
|---|---|---|---|
| Burleigh Heads | 4220 | A | Primary reference suburb |
| Miami | 4220 | A | High-demand coastal |
| Mermaid Beach | 4218 | A | Premium coastal |
| Nobby Beach | 4218 | A | Boutique coastal |
| Palm Beach | 4221 | A | Growth coastal |
| Broadbeach Waters | 4218 | A | Canal, premium |
| Isle of Capri | 4217 | A | Canal, Surfers |
| Mermaid Waters | 4218 | B | Canal, family |
| Clear Island Waters | 4226 | B | Lake, family |
| Varsity Lakes | 4227 | B | Lake, family, schools |
| Robina | 4226 | B | Infrastructure, schools |
| Currumbin | 4223 | B | Hinterland fringe |
| Tallebudgera | 4228 | B | Hinterland, acreage |
| Mudgeeraba | 4213 | C | Hinterland, large blocks |
| Coomera | 4209 | C | North GC, growth |
| Helensvale | 4212 | C | North GC, infrastructure |

### 7.2 School Reference Data

The following schools must be seeded before the school scoring module is active:

**Private Schools (complete metric seeding)**:
- Somerset College (Mudgeeraba) — ACARA ID to be confirmed
- All Saints Anglican School (Merrimac)
- St Andrew's Lutheran College (Tallebudgera)
- Emmanuel College (Carrara)
- King's Christian College (Reedy Creek)

**State Schools (complete metric seeding)**:
- Varsity College (Miami)
- Palm Beach-Currumbin State High School
- Robina State High School
- Helensvale State High School
- Elanora State High School

**Primary Schools** (catchment seeding, partial metrics):
- Burleigh Heads State School
- Miami State School
- Varsity Lakes State School
- Robina State School

### 7.3 Lifestyle Asset Categories

The following POI categories must be seeded into `lifestyle_asset_categories`:
- cafe_restaurant, gym_fitness, pilates_yoga, park_reserve, beach_access_point, swimming_pool_public, shopping_centre, childcare_centre, medical_gp, supermarket

### 7.4 Lifestyle POI Data for Key Suburbs

Initial POI counts should be seeded for Tier A suburbs (8 suburbs) before launch. Tier B and C suburbs can be populated by the first monthly refresh job.

### 7.5 System Configuration Records

- Family Fit Score weighting matrix (how Community/Lifestyle/School/Property/Financial weights combine)
- Scoring model version (to track when scoring changes require re-evaluation)
- Gold Coast destination coordinates (Burleigh Heads CBD, Broadbeach, Gold Coast Airport, key beaches)

---

## 8. Data Integration Dependency Graph

The following dependencies must be satisfied before calculations can proceed:

```
Level 0 — Must exist before anything:
  suburbs table populated
  schools table populated
  lifestyle_asset_categories seeded

Level 1 — Depends on Level 0:
  suburb_metrics (depends on: suburbs, ABS data, QPS crime data)
  suburb_lifestyle_assets (depends on: suburbs, OSM/Google POI data)
  school_metrics (depends on: schools, ACARA data)
  school_catchments (depends on: suburbs + schools)

Level 2 — Depends on Level 1:
  suburb scores calculated (community_score, lifestyle_score)
  school scores calculated (school_score)

Level 3 — Depends on Level 0 + user exists:
  family, family_members created (via Clerk onboarding)
  properties ingested (depends on: suburbs existing)

Level 4 — Depends on Level 2 + Level 3:
  property_evaluations (depends on: property + suburb scores + school scores)
  evaluation_scores (depends on: property_evaluations)

Level 5 — Depends on Level 4:
  recommendations (depends on: evaluation_scores + family_preferences)
  family_fit_score (depends on: all sub-scores + family preference weights)

Level 6 — Continuous, depends on Level 5:
  preference_events (captured constantly)
  preference learning (depends on: preference_events → updates family_preferences)
  memory consolidation (depends on: family_preferences, memory_events)
  re-evaluation trigger (depends on: preference weight changes → re-runs Level 4)
```

**Critical path for first launch**: Suburbs seeded → School data seeded → Suburb metrics calculated → First family created → First property ingested → First evaluation run.

Estimated time to reach first evaluation with correct data: 2–3 days of seeding and ETL work before first production user.

---

*Document prepared for Gold Coast Move OS engineering. Version 1.0. Last updated June 2026.*
