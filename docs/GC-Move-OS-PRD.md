# Gold Coast Move OS — Product Requirements Document
**Version**: 1.0  
**Date**: 20 June 2026  
**Status**: Implementation-Ready Draft  
**Author**: Product (AI-assisted)  
**Audience**: Engineering, Design, Founding Team

---

## Table of Contents

1. Executive Summary
2. Problem Statement
3. Product Vision & Mission
4. Target Users & Personas
5. Product Scope
6. User Stories
7. Functional Requirements
8. Non-Functional Requirements
9. Acceptance Criteria
10. Assumptions & Dependencies
11. Risks & Mitigations
12. Success Metrics
13. Roadmap
14. Open Questions

---

## 1. Executive Summary

Gold Coast Move OS is an AI-powered Family Decision Intelligence Platform that transforms one of the most consequential decisions a family will ever make — relocating — from a stressful, fragmented, and gut-feel-driven process into a structured, data-informed, and emotionally intelligent experience. The platform aggregates suburb intelligence, property data, school research, and lifestyle factors into a unified scoring engine, then uses an AI advisor to translate that data into honest, human advice calibrated to a specific family's values and priorities.

The MVP is purpose-built for one family — Ronnie and Susie — making the move to the Gold Coast. Every feature is designed around their specific needs: Ronnie's desire for community and entrepreneurial energy, Susie's requirement for a beautiful modern home with beach access, and Austin's need for the right school environment and friendships. This hyper-personalised starting point is not a limitation — it is the proof of concept. A system that genuinely serves one family well will serve any family well, because the architecture is persona-driven and configurable from the ground up.

The platform is not a property portal. It does not compete with realestate.com.au or Domain. It sits above those tools as the decision layer — ingesting their listings, interpreting them through the lens of a family's values, and telling that family whether a given property and suburb will likely improve their life in five years. The core product question is always: "Will this family have a better life here?" Every feature should reinforce that question or it should not be built.

---

## 2. Problem Statement

### What families face today

Relocating a family is a multi-month research project that touches property, schools, community, lifestyle, and finances simultaneously. The existing tool landscape forces families to manage this across five or more disconnected platforms: property portals (Domain, realestate.com.au), suburb profile tools (RP Data, Suburb Trends), school comparison sites (MySchool, individual school websites), Google Maps for commute checking, and spreadsheets or notes apps to hold it all together.

The result is decision paralysis, information overload, and decisions ultimately made on gut feel anyway — because no tool synthesises across all dimensions. Families save 40 properties and lose track of why they saved them. They inspect a home they love aesthetically, only to discover it is in a flight path. They move to a suburb with a great school but no community they connect with. They optimise for price and regret it within two years.

### Why existing solutions fail

**Property portals** (Domain, realestate.com.au) are designed for volume and agent revenue, not family decision quality. They surface properties by price and suburb, with no understanding of what a family actually values. They have no memory of your preferences. They do not tell you whether a suburb fits your lifestyle or whether the street is safe.

**Suburb data tools** (RP Data, CoreLogic, Suburb Trends) are built for investors. They optimise for capital growth potential, rental yield, and price trends. They have no opinion on whether a suburb is a good place to raise a child or build a community.

**School comparison sites** (MySchool, BetterEducation) rank schools on NAPLAN performance. They do not evaluate student wellbeing, parent community quality, confidence-building culture, or long-term pathway alignment — the things that actually matter for a family making a 10-year school choice.

**AI chatbots** (generic ChatGPT usage) are stateless, have no persistent family memory, and cannot access live property data. They are useful for one-off questions but cannot track decision evolution or build preference models.

**The gap**: No platform exists that synthesises property, suburb, school, community, and lifestyle data through the lens of a specific family's values, maintains persistent memory of that family's evolving preferences, and provides honest, advisor-grade recommendations calibrated to what will make that family's life better.

---

## 3. Product Vision & Mission

**Vision**: Every family making a major relocation decision deserves a trusted advisor who knows them deeply, interprets data through their values, and gives them the confidence to make the right choice.

**Mission**: Build the world's first AI-powered Family Decision Intelligence Platform — starting with the Gold Coast, scaling to any major relocation decision, anywhere.

**Core philosophy**: Optimise for life quality, not transaction volume. The platform succeeds when families make better decisions, not when they click more properties.

**What we are**: A trusted relocation advisor.  
**What we are not**: A property portal, a suburb data tool, or a generic AI assistant.

**Weighting Philosophy**: The platform's scoring engine encodes the belief that community and lifestyle matter more than property spec and price. This is a deliberate, values-based design decision. It should be surfaced transparently to users, not hidden in the algorithm.

---

## 4. Target Users & Personas

### Design Principle: Personas Are Onboarding-Driven

**The platform does not have hardcoded personas.** Every persona in the system — the primary decision maker, co-decision maker, children, and pets — is created dynamically from data captured during the family onboarding flow. The AI advisor, scoring engine, and per-member commentary all reference the family's own profile data, not a fixed set of names or priorities.

The Altit family (Ronnie, Susie, Austin, Mabel) is the MVP validation case. Their profile was the design input. But the product architecture treats them as a data instance, not a template.

**What onboarding captures per family member:**
- Name
- Age
- Role: `primary_adult` | `secondary_adult` | `child` | `pet`
- Top priorities (selected from a curated list + free text)
- Non-negotiables (property requirements)
- School concerns (for child members)
- Pet requirements (for pet members)

The system then uses these profiles to generate all per-member commentary, all preference learning, and all AI advisor context. "What Ronnie will like" becomes "What [Primary Adult Name] will like" for any family.

---

### Persona Archetypes (Generic — Derived from Onboarding)

#### Persona Type 1: Primary Decision Maker (Adult)

The primary account holder. Initiates onboarding, manages family settings, receives notifications, and typically uses the platform most actively. Generally research-oriented and data-comfortable. Their role is to drive the decision process.

**Key job-to-be-done**: "Tell me, honestly, whether this suburb and home will improve my family's life."

**Platform behaviour**: Daily dashboard user during active search. Uses the AI Advisor to stress-test shortlisted options. Reviews Decision Journal. Manages the shortlist.

**Design implications**: Needs at-a-glance scoring, clear recommendation signals, and deep-dive reports on demand. Should feel like talking to a smart advisor, not reading a spreadsheet.

#### Persona Type 2: Co-Decision Maker (Adult)

Has their own account linked to the same family. May have different priorities to the primary user — often more aesthetic, emotional, or lifestyle-driven than data-driven. Will evaluate properties through their own lens.

**Key job-to-be-done**: "Show me what my daily life will look and feel like in this home and suburb."

**Platform behaviour**: Focuses on individual property reports, especially per-person commentary tailored to their profile. Less interested in suburb data tables; more interested in lifestyle narratives and visual quality of properties.

**Design implications**: The platform must reflect their individual preferences back to them, not surface a generic family view. Their onboarding priorities drive their personal section of every property evaluation.

#### Persona Type 3: Child (Indirect Stakeholder)

Not a platform user. Represented through their parent's family member profile entry. Their priorities (friendships, school confidence, outdoor activity, independence) are encoded during onboarding and drive School Score weighting and the Five-Year Fit Score child sub-dimensions.

**Platform role**: The School Fit Score and Five-Year Fit Score's child dimension are computed on their behalf. The AI Advisor references their profile in school and suburb recommendations.

#### Persona Type 4: Pet (Environmental Stakeholder)

Not a platform user. Pet requirements (yard size/quality, walkability, park proximity, traffic safety) are captured during onboarding and scored as sub-dimensions within the Lifestyle and Property scores.

**Platform role**: Yard suitability is a property evaluation criterion. Dog-friendly parks and off-leash areas are lifestyle POI categories. Including pets is not whimsical — it reflects the reality that pet needs materially affect suburb and property suitability.

---

### MVP Validation Family: Altit Family (Pre-seeded Test Profile)

For MVP, one family profile will be pre-configured as the test and validation case:

| Member | Role | Age | Key Priorities |
|---|---|---|---|
| Ronnie | Primary Adult | 55 | Better lifestyle, strong community, school ecosystem, entrepreneurial peer group, wellness |
| Susie | Secondary Adult | 45 | Beautiful modern home, beach access, wellness (cafes, pilates), aesthetic appeal, pride of ownership |
| Austin | Child | 7 | Friendships, confidence, positive school experience, outdoor lifestyle |
| Mabel | Pet (Groodle) | — | Suitable yard, walkability, parks, safe environment |

This profile is a data instance in the database, not a design pattern baked into the code. All platform features must work identically for any family who completes onboarding.

---

## 5. Product Scope

### MVP In Scope (Phase 1)

- Family profile creation and onboarding (capturing personas, priorities, budget — see Open Questions)
- Property submission via URL paste (realestate.com.au / domain.com.au) + AI extraction
- AI scoring engine: Family Fit Score, Community Score, Lifestyle Score, School Score, Property Score, Financial Score
- Five-Year Fit Score and Confidence Score
- Dashboard with property feed and sorted shortlist
- Property Evaluation Report (full breakdown per property)
- AI Advisor — conversational interface with family memory
- Decision Journal — auto-generated per property review, editable
- Suburb Intelligence — Tier A/B/C classification for target suburbs
- School Intelligence — Somerset College and All Saints evaluation
- Preference Learning — PreferenceEvent capture from all interactions
- Family Memory system — permanent, preference, learned, session, decision types
- Notifications — Daily Brief email via Resend
- Inspection Tracker — basic status tracking per property
- Risk System — flood, road noise, aircraft noise, crime, development flags
- Authentication via Clerk — multi-user family accounts. Primary user creates family and invites co-decision maker (e.g., partner) via email. Both have their own Clerk accounts with shared access to all family data, with individual preference profiles tracked separately.
- Responsive web app (Next.js) — desktop-primary, mobile-usable

### MVP Out of Scope (Phase 1)

- Native mobile app (iOS/Android) — responsive web only in MVP
- Native mobile app (iOS/Android)
- PropTrack API integration (deferred to Phase 2)
- Automated property discovery (scraping/monitoring listings without URL paste)
- Mortgage/finance calculator or broker integration
- Conveyancing or contract management
- Removal/logistics planning
- Neighbourhood social network or community forum features
- Integration with real estate agents
- Video or 3D tour embedding
- Public suburb profiles (no public-facing pages in MVP)

### Phase 2 (Post-MVP)

- PropTrack API integration for automated property data ingestion
- Multi-user family accounts (Susie's own login, separate preference profile)
- Property alert monitoring (automated daily scan for new listings matching criteria)
- Expanded suburb coverage beyond Gold Coast
- Comparative "city vs city" relocation analysis
- Agent CRM integration (flag properties to a buyer's agent)
- Mobile-responsive design upgrade to PWA

### Phase 3 (Scale)

- Platform generalisation — any family, any city
- White-label for buyer's agents and relocation consultants
- PropTrack / CoreLogic API data enrichment
- Community data partnerships (local council data, ABS Census API)
- School data partnerships (direct ACARA integration)
- Financial modelling (stamp duty, mortgage scenarios, rental yield for investment properties)

---

## 6. User Stories

### Onboarding

1. As Ronnie, I want to create a family account with our names, ages, and priorities, so that the platform understands who we are before it evaluates anything.
2. As Ronnie, I want to be asked for our budget range during onboarding, so that the platform can flag properties outside our financial capacity.
3. As Ronnie, I want to specify our non-negotiable property requirements (pool, home office, detached house, AC), so that properties missing these are automatically filtered or flagged.
4. As Susie, I want to enter my personal priorities (aesthetic, beach, wellness) separately from Ronnie's, so that the platform knows what matters to each of us.
5. As Ronnie, I want to specify our target suburbs and school preferences, so that the platform can pre-configure suburb tiers and school shortlist.
6. As Ronnie, I want the platform to flag any critical information gaps (like missing budget) during onboarding, so that I know what data to provide before the scores become reliable.
7. As Ronnie, I want to set our move timeline (target move date), so that the platform can prioritise urgency in recommendations.

### Property Submission & Ingestion

8. As Ronnie, I want to paste a realestate.com.au or domain.com.au URL and have the system extract all property details automatically, so that I don't have to manually enter data from listings.
9. As Ronnie, I want to see a confirmation screen showing what was extracted, so that I can correct any AI extraction errors before scoring runs.
10. As Ronnie, I want the system to detect if I paste a duplicate URL (already in my shortlist), so that I'm not creating duplicate entries.
11. As Ronnie, I want to manually add or override extracted property fields (e.g., correct an extracted bedroom count), so that inaccurate source data doesn't corrupt my scores.
12. As Ronnie, I want to add personal notes at the time of property submission ("noticed from Google Maps it's near a busy road"), so that my real-world observations are captured alongside the extracted data.

### AI Scoring Engine

13. As Ronnie, I want every property to receive a Family Fit Score out of 100 within 30 seconds of submission, so that I get a fast signal on whether it's worth investigating further.
14. As Ronnie, I want to see each sub-score (Community, Lifestyle, School, Property, Financial) broken down separately, so that I understand which dimensions are strong and which are weak.
15. As Ronnie, I want to see the Five-Year Fit Score alongside the main score, so that I'm thinking about long-term life quality, not just the property's current specs.
16. As Ronnie, I want to see a Confidence Score with each evaluation, so that I know how reliable the score is given the data available.
17. As Ronnie, I want any Critical Risks (flood zone, aircraft noise, crime cluster) to be surfaced prominently — above the score — so that dealbreakers are never buried.
18. As Ronnie, I want to understand the scoring weights and how the algorithm works, so that I trust the output rather than treating it as a black box.

### Dashboard & Property Feed

19. As Ronnie, I want a dashboard that shows all submitted properties sorted by Family Fit Score by default, so that the best-fit properties are always at the top.
20. As Ronnie, I want to filter properties by recommendation level (Prioritise / Inspect / Monitor / Ignore), so that I can focus on properties above a certain threshold.
21. As Ronnie, I want to see each property card with a photo, address, price, Family Fit Score, and one-line AI summary, so that I can scan the list quickly.
22. As Susie, I want to see a "Susie's picks" filter that shows only properties flagged as matching my priorities, so that I can review the list through my own lens.
23. As Ronnie, I want to sort by different dimensions (Property Score, Community Score, price), so that I can explore the list from different angles.
24. As Ronnie, I want to archive or hide properties I've decided to reject, so that my active list stays clean.

### Property Evaluation Report

25. As Ronnie, I want a full-page property evaluation report for each submitted property, showing all scores, explanations, risks, and AI narrative, so that I have a complete picture before deciding whether to inspect.
26. As Susie, I want the Property Evaluation Report to include an AI-written "day in the life" narrative — what our daily routine would look like from this address — so that I can emotionally evaluate the fit.
27. As Ronnie, I want the report to include a Google Maps travel time analysis (to Burleigh Heads, nearest beach, Somerset College, All Saints), so that I can verify the location meets our 20-minute proximity requirements.
28. As Ronnie, I want to be able to add comments and a personal rating (1–5) to each property evaluation, so that my reactions are captured alongside the AI analysis.
29. As Ronnie, I want to see a side-by-side comparison view for 2–3 shortlisted properties, so that I can evaluate trade-offs directly.

### AI Advisor

30. As Ronnie, I want to chat with an AI relocation advisor that knows our family profile and property shortlist, so that I can ask natural-language questions like "which suburb has the best community for us?"
31. As Ronnie, I want the AI Advisor to remember decisions and preferences I've expressed in past sessions, so that I don't have to re-explain context every time.
32. As Ronnie, I want to ask the AI Advisor to compare two specific properties and get a clear recommendation with reasoning, so that I can get a second opinion on a difficult choice.
33. As Ronnie, I want the AI Advisor to proactively flag things I haven't considered ("You haven't asked about commute time from this property to the airport"), so that I benefit from advisor-grade thinking, not just data retrieval.
34. As Ronnie, I want the AI Advisor to explain its reasoning in plain English, not in technical scoring language, so that the output is useful for conversations with Susie.

### Decision Journal

35. As Ronnie, I want a Decision Journal entry to be automatically created every time I rate or comment on a property, so that my evolving views are captured without manual effort.
36. As Ronnie, I want to write freeform journal entries about a property or suburb (impressions from an inspection, a conversation with a local), so that qualitative insights are stored alongside quantitative data.
37. As Ronnie, I want the system to detect decision drift — if I've changed my view on a property significantly — and surface that to me, so that I can reflect on why my opinion changed.
38. As Ronnie, I want to export my Decision Journal for a property as a PDF summary, so that Susie and I can review it offline or share it with our buyer's agent.

### Preference Learning

39. As Ronnie, I want the system to learn my preferences from my interactions (saves, rejects, comments, ratings), so that scores become more personalised over time without manual configuration.
40. As Susie, I want the system to separately track my preference signals, so that the platform understands Ronnie and I may weight things differently.
41. As Ronnie, I want to see a "Your Preference Profile" summary showing what the system has learned about our priorities, so that I can verify it's accurate and correct it if not.

### School Evaluation

42. As Ronnie, I want a dedicated School Intelligence page for Somerset College and All Saints, covering wellbeing, community, academic outcomes, commute, and pathway, so that we can make a properly informed school choice alongside our suburb choice.
43. As Ronnie, I want the School Score to incorporate commute time from each property we're evaluating, so that school proximity is factored into the overall property score dynamically.
44. As Ronnie, I want the platform to clearly recommend which school is the better fit for Austin specifically (not generically), based on our stated priorities around confidence and friendships, so that the recommendation is personalised.

### Suburb Comparison

45. As Ronnie, I want a Suburb Intelligence page showing each target suburb rated Tier A, B, or C with reasoning, so that I understand which suburbs are in play and which to avoid.
46. As Ronnie, I want to compare two suburbs head-to-head across all scoring dimensions, so that I can understand the trade-offs clearly.

### Notifications

47. As Ronnie, I want to receive a Daily Brief email each morning listing new properties that match our criteria, so that I don't have to manually check the platform every day.
48. As Ronnie, I want to receive an alert when a property on my shortlist has a price change or status change (sold, under offer), so that I can act quickly if needed.

### Inspection Tracker

49. As Ronnie, I want to log an inspection date for any property on my shortlist, so that we can plan our inspection schedule.
50. As Ronnie, I want to record inspection notes and an updated rating after we've physically visited a property, so that post-inspection impressions are captured and tracked against pre-inspection scores.

---

## 7. Functional Requirements

### 7.1 Family Profile & Onboarding

**FR-ONB-001**: The onboarding flow must capture the following data points before any scoring is available:
- Family name
- Family members (name, age, role: adult/child/pet)
- Per-adult: top priorities (ranked selection from predefined list + free text)
- Target move timeframe
- Non-negotiable property requirements (checklist)
- Strong preference list (checklist)
- Target suburbs (multi-select from Gold Coast suburb list)
- School preferences (multi-select from school shortlist)
- Budget min/max (CRITICAL GAP: see Open Questions — must be captured or scoring is unreliable)
- Current city/state (for contextual comparisons)

**FR-ONB-002**: If budget is not provided during onboarding, the platform must display a persistent warning banner on the dashboard and in all Financial Score displays indicating that financial scoring is unavailable.

**FR-ONB-003**: Onboarding must be completable in under 10 minutes. Long-form questions must be optional on first pass, with prompts to complete them later.

**FR-ONB-004**: Family profile must be editable at any time from a dedicated **Family Inputs** page, with all scores flagged for recalculation on next evaluation if inputs change.

**FR-ONB-004a — Family Inputs Page**: A dedicated editable section (accessible from main navigation as "Settings" or "Family Inputs") must allow the family to update at any time:
- Budget minimum and maximum (in AUD)
- Move timeframe (month/year target)
- Non-negotiable property requirements
- Strong preferences list
- Target suburb tier selections
- School preferences
- Scoring weight adjustments (advanced)
This is distinct from the onboarding flow — it is a persistent, always-editable source of truth for the family's inputs. Changes here propagate to all future evaluations. The budget fields must be prominently surfaced here, as they are the most likely input to change during the search process.

**FR-ONB-005 — Multi-User Family Accounts**: The platform supports multiple Clerk accounts linked to a single family record.
- The **primary user** creates the family during onboarding and is the family owner.
- The primary user can **invite additional family members** (e.g., a partner) by entering their email. The invited user receives an email with a unique invite link (valid 7 days). On accepting, they sign up via Clerk and are linked to the family.
- All linked users see the **same shared family data**: properties, evaluations, decision journal, suburb intelligence, school intelligence, shortlist.
- Each user has their **own preference profile**, tracked separately within the shared family context. The AI advisor knows which user is currently logged in and adjusts per-person commentary accordingly.
- Notifications (Daily Brief) are sent to **all linked users individually**.
- The primary user can remove other users from the family account via the Family Inputs page.
- MVP supports up to **3 users per family**.

**FR-ONB-006**: Preference weights are configurable. The default scoring weights (Community 25%, Lifestyle 20%, School 20%, Property 20%, Financial 15%) must be surfaced in the Family Inputs page and editable via an advanced settings panel. Weight changes must total 100%.

### 7.2 Property Submission & Ingestion

**FR-PROP-001**: The property submission interface must accept a URL from realestate.com.au or domain.com.au. Property data is extracted using **Apify** (apify.com) — a managed web scraping platform with purpose-built actors for both REA and Domain that returns structured JSON directly, without requiring raw HTML parsing or AI extraction for basic fields. This replaces the earlier approach of fetching HTML with httpx and using OpenAI to extract fields. OpenAI is still used downstream for qualitative scoring and narrative generation, but not for field extraction. Apify handles anti-bot protection, JavaScript rendering, and structured output. The following fields must be extracted:
- Address (street, suburb, state, postcode)
- Price (listed price or price range)
- Bedrooms, bathrooms, car spaces
- Property type (house, townhouse, unit)
- Land size (m²)
- House size (m²)
- Pool (yes/no/unknown)
- Air conditioning (yes/no/unknown)
- Home office (yes/no/inferred)
- Garage/car accommodation
- Property description (raw text)
- Agent name and agency
- Listed date
- All image URLs

**FR-PROP-002**: The extraction must use a structured prompt with JSON output schema. If a field cannot be extracted with confidence, it must be returned as `null` rather than guessed.

**FR-PROP-003**: After extraction, the system must display a confirmation screen ("Did we get this right?") allowing the user to correct any field before proceeding to scoring.

**FR-PROP-004**: Duplicate URL detection: if the same URL is submitted a second time, display a warning with a link to the existing property entry. Do not create a duplicate.

**FR-PROP-005**: Image storage: extracted image URLs must be stored. Images are not proxied or stored locally in MVP — URLs are used directly. If an image URL becomes invalid, fall back to a placeholder.

**FR-PROP-006**: Manual property creation must be supported as a fallback for cases where URL extraction fails (off-market properties, private sales).

**FR-PROP-007**: Each property record must store: submission timestamp, submitting user, source URL, raw extracted JSON, corrected field values, user notes at submission time, and scoring run history.

### 7.3 AI Scoring Engine

**FR-SCORE-001**: The scoring engine must compute the Family Fit Score using the following formula:
```
FamilyFitScore = (CommunityScore × 0.25) + (LifestyleScore × 0.20) + (SchoolScore × 0.20) + (PropertyScore × 0.20) + (FinancialScore × 0.15)
```
Each sub-score is on a 0–10 scale. The final score is normalised to 0–100.

**FR-SCORE-002**: Community Score sub-dimensions and weights:
- Owner occupier rate: 30%
- Family density: 20%
- Educational attainment: 15%
- Median household income: 15%
- Crime and safety: 15%
- Community engagement: 5%
Data source MVP: ABS Census data (2021), QPS crime statistics where available, cached in PostgreSQL.

**FR-SCORE-003**: Lifestyle Score sub-dimensions and weights:
- Burleigh Heads access (travel time via Google Maps): 25%
- Beach access (travel time to nearest patrolled beach): 20%
- Wellness infrastructure (pilates studios, gyms, health food cafes within 5km): 20%
- Cafe and dining (quality cafes within 2km, sourced from Google Places): 15%
- Outdoor recreation (parks, trails, dog-friendly areas within 3km): 10%
- Shopping convenience (major supermarket within 5km): 10%

**FR-SCORE-004**: School Score sub-dimensions and weights:
- Student wellbeing: 25% (sourced from ICSEA, available school survey data, AI synthesis of school reviews)
- Parent community: 20% (qualitative AI synthesis)
- Academic outcomes: 20% (NAPLAN, MySchool data)
- Commute from property (Google Maps travel time): 15%
- Extracurricular breadth: 10%
- Long-term pathway: 10% (university entrance data, career pathway programs)

**FR-SCORE-005**: Property Score sub-dimensions and weights:
- Modernity (age of construction, renovation status): 20%
- Design quality (architectural style, coastal contemporary alignment): 15%
- Indoor-outdoor flow (AI assessment from description and images): 15%
- Pool quality: 10%
- Home office suitability: 10%
- Entertaining space: 10%
- Privacy: 10%
- Block utility: 10%

**FR-SCORE-006**: Financial Score: requires budget to be set. Score is based on:
- Price vs budget (over/under/within): 40%
- Estimated stamp duty and buy-in costs: 20%
- Suburb capital growth trend (3-year): 20%
- Estimated holding costs vs comparable rent: 20%
If budget is not set, Financial Score returns `null` and is excluded from the weighted average with weights redistributed proportionally across the other four dimensions.

**FR-SCORE-007**: Five-Year Fit Score sub-dimensions and weights:
- Community belonging: 20%
- Child friendships (Austin): 15%
- Parent friendships: 15%
- Lifestyle improvement: 15%
- School fit: 15%
- Home satisfaction: 10%
- Financial comfort: 5%
- Regret risk: 5%

**FR-SCORE-008**: Confidence Score (0.0–1.0) must be computed based on:
- Number of property fields successfully extracted (vs null): 40%
- Data freshness of suburb data: 30%
- Completeness of family preference profile: 30%
A score below 0.5 must trigger a warning on the evaluation report.

**FR-SCORE-009**: Recommendation Level must be derived from Family Fit Score:
- 90–100: "Prioritise Immediately" (green, urgent indicator)
- 80–89: "Inspect" (green)
- 70–79: "Monitor" (amber)
- Below 70: "Ignore" (red/grey)

**FR-SCORE-010**: Risk flags must be evaluated for every property:
- Flood risk: sourced from Queensland Spatial Catalogue / QFlood data by suburb and street
- Road noise: proximity to arterial roads (Google Maps road type within 200m)
- Aircraft noise: proximity to Gold Coast Airport flight paths (static polygon data)
- Future development: DA (Development Application) awareness near property (deferred to Phase 2, flag as unavailable in MVP)
- Crime: suburb crime index from QPS data
- Property defects: not assessable from listing data alone — flagged as requiring independent building inspection
Critical risks (flood zone, active flight path, high crime index) must be displayed above the Family Fit Score with a block indicator.

**FR-SCORE-011**: All AI scoring calls must use GPT-4o for primary scoring and explanation generation. GPT-4o-mini may be used for sub-tasks such as formatting, summarisation of long text, and tagging.

**FR-SCORE-012**: Scoring must complete within 30 seconds for a standard property submission. Scoring runs asynchronously — the user sees a progress indicator and is notified when complete.

**FR-SCORE-013**: Suburb-level data (Community Score, Lifestyle Score) must be cached in Redis with a TTL of 7 days to avoid redundant API calls. Property-specific scoring (Property Score, Financial Score) is computed fresh per property.

### 7.4 Dashboard & Property Feed

**FR-DASH-001**: The main dashboard must display:
- Family profile summary (top bar)
- Active shortlist of properties as cards, sorted by Family Fit Score descending by default
- Quick filters: Recommendation Level, Suburb, Price Range, Bedrooms
- Sort options: Family Fit Score, Property Score, Price (asc/desc), Date Added
- Summary stats: total properties tracked, number in each recommendation tier

**FR-DASH-002**: Each property card must display:
- Primary photo
- Address and suburb
- Listed price
- Family Fit Score (large, colour-coded)
- Recommendation Level label
- One-line AI summary ("Strong lifestyle match. Pool and layout tick boxes. Monitor flood risk.")
- Status badge (Active / Under Offer / Sold / Archived)
- Date added

**FR-DASH-003**: Dashboard must update in real time when a new property is submitted and scored. Use optimistic UI — show the card immediately with a "Scoring..." state, then populate scores when complete.

**FR-DASH-004**: The dashboard must support an "Archive" action per property card that removes it from the active list without deleting the record.

**FR-DASH-005**: A "Compare" mode must allow the user to select 2–3 properties and view them side-by-side in a comparison table.

### 7.5 Property Evaluation Report

**FR-REPORT-001**: Each property must have a dedicated evaluation report page accessible from the dashboard card. The report must include:

- Header: address, price, photos (carousel), key stats
- Critical Risks block (if any) — displayed prominently at top
- Family Fit Score — large, colour-coded, with recommendation level
- Five-Year Fit Score — secondary score
- Confidence Score — with tooltip explaining what it means
- Sub-score breakdown: Community, Lifestyle, School, Property, Financial — each with score, tier, and AI explanation paragraph
- Travel time panel: distances and drive times to Burleigh Heads, nearest beach, Somerset College, All Saints
- Non-negotiables checklist: Pool, Home Office, Detached House, AC, Safe Street — pass/fail/unknown
- Strong preferences checklist: 5BR, Modern, Coastal Contemporary, Indoor-Outdoor Flow, etc. — met/unmet/unknown
- "Day in the Life" AI narrative — 2–3 paragraphs describing what a typical day for this family would look like from this address
- Decision Journal entries for this property
- User comments and rating input
- Action buttons: Book Inspection / Archive / Compare / Share

**FR-REPORT-002**: The "Day in the Life" narrative must be generated by GPT-4o using the family profile, property details, and suburb data as context. It must name family members and reference their specific priorities. It must not be generic.

**FR-REPORT-003**: Travel times must be fetched from Google Maps Distance Matrix API using driving mode as the default, with a note that times are estimates and traffic conditions vary.

**FR-REPORT-004**: The non-negotiables checklist must show "Unknown" if the extracted property data is ambiguous rather than guessing. Unknown items must be flagged as "Verify at inspection."

**FR-REPORT-005**: The report must be printable / PDF-exportable. Use browser print styles with a clean layout.

### 7.6 AI Advisor (Conversational Interface)

**FR-AI-001**: The AI Advisor must be accessible from a persistent chat interface available on all pages (slide-out panel or dedicated page). It must be contextually aware of which property or suburb the user is currently viewing.

**FR-AI-002**: The AI Advisor must have access to the following context at all times:
- Full family profile
- Complete property shortlist with scores
- Family Memory (all memory types)
- Suburb intelligence data
- School evaluation data
- Decision Journal entries

**FR-AI-003**: The AI Advisor must be built on OpenAI function calling (tool use). Define the following tools:
- `get_family_profile()` — returns current family profile
- `get_property(id)` — returns property record with scores
- `list_properties(filters)` — returns filtered property list
- `get_suburb_data(suburb_name)` — returns suburb intelligence
- `get_school_data(school_name)` — returns school evaluation
- `get_decision_journal(property_id)` — returns journal entries
- `get_family_memory(type)` — returns memories by type
- `add_memory(type, content)` — adds a new memory record
- `update_property_note(property_id, note)` — writes a note to a property

**FR-AI-004**: System prompt for AI Advisor must instruct the model to: act as a trusted relocation advisor, use the family's real names, reference specific property addresses when comparing, be honest when data is insufficient, proactively surface risks, and end advice with a clear recommendation rather than a balanced non-answer.

**FR-AI-005**: Conversation history must be stored per session. Sessions are linked to the family account. The AI must reference previous sessions where relevant ("Last week you said you were concerned about the Mermaid Waters property — has that changed?").

**FR-AI-006**: The AI Advisor must have a "Challenge my thinking" mode where the user can ask the AI to argue against their current front-runner property to stress-test the decision.

### 7.7 Decision Journal

**FR-DJ-001**: A Decision Journal entry must be automatically created when:
- A property is submitted (entry type: "First look")
- A user adds a rating or comment to a property (entry type: "Reaction")
- An inspection is logged (entry type: "Post-inspection")
- An AI Advisor conversation references a property (entry type: "AI discussion")

**FR-DJ-002**: Each Journal entry must store: timestamp, entry type, property ID, author (Ronnie / Susie), content (auto-generated or user-written), rating at time of entry, and AI-generated summary.

**FR-DJ-003**: Decision drift detection: if a user's rating of a property changes by 2+ points between entries, the system must flag this as "Decision Drift Detected" and prompt the user to journal the reason for the change.

**FR-DJ-004**: The journal for each property must be viewable as a timeline, showing the evolution of opinion from first look to current view.

**FR-DJ-005**: Journal entries must support freeform text editing. Auto-generated entries are editable. Edits are versioned (original preserved, edits tracked).

### 7.8 Suburb Intelligence

**FR-SUB-001**: The platform must pre-populate suburb intelligence for the following Gold Coast suburbs: Robina, Mermaid Waters, Varsity Lakes, Clear Island Waters, Burleigh Heads, Burleigh Waters, Palm Beach, Currumbin, Broadbeach Waters, Benowa, Bundall, and any additional suburbs added by the user.

**FR-SUB-002**: Each suburb must be classified into a tier:
- Tier A: Core — strongly aligned with family profile, actively evaluate properties here
- Tier B: Conditional — good fit on some dimensions, evaluate selectively based on specific property quality
- Tier C: Avoid — misaligned with family profile or has disqualifying risks

**FR-SUB-003**: The Suburb Intelligence page must display for each suburb:
- Tier classification with rationale
- All five sub-scores (Community, Lifestyle, School, Property, Financial)
- Key strengths (top 3 bullet points)
- Key weaknesses (top 3 bullet points)
- Properties currently on shortlist in this suburb
- AI-generated suburb narrative

**FR-SUB-004**: Suburb comparison view must allow selecting two suburbs and displaying a side-by-side table across all scoring dimensions.

**FR-SUB-005**: Suburb data must be refreshed from source (ABS, QPS, Google Places) no more than once per 7 days. Manual refresh must be available to administrators.

### 7.9 School Intelligence

**FR-SCH-001**: The platform must include dedicated evaluation profiles for:
- Somerset College (Mudgeeraba)
- All Saints Anglican School (Merrimac/Banora Point — confirm campus)

**FR-SCH-002**: Each school profile must include:
- School Score (0–10) using sub-dimension weights from FR-SCORE-004
- ICSEA value (Index of Community Socio-Educational Advantage)
- NAPLAN performance summary (Reading, Numeracy — relative to similar schools)
- Enrolment size and student-to-teacher ratio
- Co-curricular highlights (sports, arts, STEM, community)
- University pathway outcomes (where available)
- School values and culture narrative (AI-synthesised from available sources)
- Commute time from each shortlisted property (dynamic, via Google Maps API)
- Parent community notes (qualitative AI synthesis — clearly labelled as estimated/qualitative)
- AI recommendation: which school better fits Austin's profile and why

**FR-SCH-003**: School Score must dynamically recalculate the commute sub-dimension for each property when displayed within a Property Evaluation Report.

**FR-SCH-004**: School data must be sourced from: MySchool (ACARA public data), school official websites, and AI synthesis of publicly available reviews and community information. All qualitative data must be clearly labelled as AI-synthesised with confidence caveats.

### 7.10 Preference Learning

**FR-PREF-001**: Every user interaction that implies a preference must create a PreferenceEvent record:
- Property saved: positive signal
- Property archived/rejected: negative signal
- Rating given: scaled signal (1 = strong negative, 5 = strong positive)
- Comment text: NLP-tagged for attribute mentions
- AI Advisor conversation: extracted preference signals via GPT-4o-mini

**FR-PREF-002**: PreferenceEvent schema:
```
{
  id: uuid,
  family_id: uuid,
  user_role: "primary" | "secondary",
  event_type: "save" | "reject" | "rate" | "comment" | "ai_signal",
  property_id: uuid | null,
  suburb: string | null,
  attribute: string,           // e.g. "pool", "modern_design", "quiet_street"
  signal_direction: "positive" | "negative" | "neutral",
  signal_strength: 0.0–1.0,
  source_text: string | null,  // raw text if from comment/AI
  timestamp: datetime
}
```

**FR-PREF-003**: The preference model must produce a ranked attribute importance list per user. This list must be displayed in a "Preference Profile" page and must be used to modulate scoring weights in future scoring runs.

**FR-PREF-004**: If learned preferences conflict with stated preferences (e.g., the user stated "5 bedrooms is a strong preference" but consistently rejects properties with 5 bedrooms that are otherwise costly), the system must surface this conflict to the user for resolution.

### 7.11 Family Memory

**FR-MEM-001**: The Family Memory system must support five memory types:

| Type | Description | Retention |
|---|---|---|
| Permanent | Core family facts (names, ages, priorities) | Indefinite, manual edit only |
| Preference | Stated and learned preferences | Indefinite, updated on new signals |
| Learned | Patterns inferred from behaviour (not explicitly stated) | 90 days rolling window |
| Session | Context from the current advisor session | Current session only |
| Decision | Key decisions made (e.g., "Rejected 12 X St because of road noise") | Indefinite |

**FR-MEM-002**: Memory records must be injected into the AI Advisor system prompt on every new conversation, within token limits. If total memory exceeds token limits, priority order is: Permanent > Decision > Preference > Learned > Session.

**FR-MEM-003**: Users must be able to view, edit, and delete any memory record from a Family Memory page in Settings.

**FR-MEM-004**: The AI Advisor must be able to add new memory records during conversation via the `add_memory` function tool when the user makes a significant statement (e.g., "We've decided the 5th bedroom isn't necessary" → creates a Decision memory).

### 7.12 Notifications & Daily Brief

**FR-NOTIF-001**: A Daily Brief email must be sent to the family's registered email address each morning at a user-configurable time (default: 7:30 AM AEST).

**FR-NOTIF-002**: Daily Brief content must include:
- Number of new properties submitted or flagged in the last 24 hours
- Top 3 properties by Family Fit Score (with scores and one-line summaries)
- Any properties that have changed status (Under Offer, Sold, Price Reduced)
- One suburb intelligence update or insight (rotated daily)
- A prompt to review pending journal entries if any exist

**FR-NOTIF-003**: Email must be sent via Resend API. Template must be responsive and brand-consistent. Must render cleanly in Gmail, Apple Mail, and Outlook.

**FR-NOTIF-004**: Users must be able to opt out of the Daily Brief from within the email (one-click unsubscribe) or from Settings.

**FR-NOTIF-005**: In-app notifications must be supported for: new score available, critical risk detected on a saved property, property status change (if detectable).

### 7.13 Inspection Tracker

**FR-INSP-001**: Any property can have an inspection logged. Inspection record must capture:
- Inspection date and time
- Inspection type (open home / private)
- Attendees (Ronnie / Susie / both)
- Pre-inspection checklist (auto-generated from non-negotiables and strong preferences)
- Post-inspection notes (freeform)
- Post-inspection rating (1–5)
- Post-inspection recommendation (Proceed / Hold / Reject)

**FR-INSP-002**: The inspection pre-checklist must include all non-negotiable requirements and strong preferences, formatted as a printable checklist the family can take to the inspection.

**FR-INSP-003**: Post-inspection data must automatically create a Decision Journal entry of type "Post-inspection."

**FR-INSP-004**: The Inspection Tracker must display a calendar view of upcoming inspections and a history of past inspections.

---

## 8. Non-Functional Requirements

### Performance

- **NFR-PERF-001**: Initial page load (dashboard) must complete in under 2 seconds on a standard broadband connection (50 Mbps).
- **NFR-PERF-002**: AI scoring (full Family Fit Score) must complete within 30 seconds.
- **NFR-PERF-003**: AI Advisor response must begin streaming within 3 seconds of user message submission.
- **NFR-PERF-004**: Google Maps travel time lookups must complete within 5 seconds per property.
- **NFR-PERF-005**: Redis caching must be used for all suburb-level data with a minimum 7-day TTL.

### Security

- **NFR-SEC-001**: All authentication managed via Clerk. JWT tokens used for API calls. Token expiry: 1 hour. Refresh token: 30 days.
- **NFR-SEC-002**: All API endpoints must validate the family_id from the JWT against the requested resource. No family should ever be able to access another family's data.
- **NFR-SEC-003**: All data at rest in PostgreSQL must be encrypted. Managed by Railway's built-in encryption.
- **NFR-SEC-004**: All data in transit must use HTTPS/TLS. No plain HTTP endpoints.
- **NFR-SEC-005**: OpenAI API key must be stored as an environment variable, never in code or client-side.
- **NFR-SEC-006**: User input must be sanitised before use in AI prompts to prevent prompt injection.
- **NFR-SEC-007**: Sentry must be configured for error monitoring on both frontend and backend. PII must be scrubbed from Sentry payloads.

### Scalability

- **NFR-SCALE-001**: The database schema must be multi-tenant from day one. All records must include a `family_id` foreign key.
- **NFR-SCALE-002**: The system must be designed to support 100 concurrent family accounts without architectural changes.
- **NFR-SCALE-003**: Background job processing (scoring runs, email dispatch) must use an async task queue (FastAPI BackgroundTasks in MVP; migrate to Celery/Redis Queue in Phase 2 if needed).

### Accessibility

- **NFR-A11Y-001**: All UI components must meet WCAG 2.1 AA standards.
- **NFR-A11Y-002**: Colour-coded scores (green/amber/red) must include a text label and not rely on colour alone.
- **NFR-A11Y-003**: All form inputs must have associated labels. Error messages must be associated with their input.

### Reliability

- **NFR-REL-001**: Target uptime: 99.5% (MVP). This is a single-family tool in MVP — high availability is important but not mission-critical.
- **NFR-REL-002**: All external API calls (OpenAI, Google Maps, Resend) must have retry logic with exponential backoff (max 3 retries).
- **NFR-REL-003**: If OpenAI API is unavailable, property submission must queue the scoring run and notify the user when complete. The UI must never appear broken due to a failed AI call.
- **NFR-REL-004**: Database backups must run daily (managed by Railway).

---

## 9. Acceptance Criteria

### AC-ONB-001: Onboarding Complete
PASS: A new user can complete the full onboarding flow in under 10 minutes and have a functional family profile. The dashboard loads with no errors. A budget warning banner displays if budget was not entered.

### AC-PROP-001: Property Submission via URL
PASS: User pastes a valid realestate.com.au URL. Within 15 seconds, a confirmation screen displays with at least 10 of the 17 target fields populated correctly. The user can edit any field. Submission completes and a scoring job is queued.
FAIL: Any of the following — system returns error, fewer than 8 fields extracted, extracted data is structurally wrong, no confirmation screen shown.

### AC-SCORE-001: Scoring Engine Produces Valid Output
PASS: Within 30 seconds of submission, a Family Fit Score (0–100), all five sub-scores (0–10), a Five-Year Fit Score (0–100), and a Confidence Score (0.0–1.0) are available. If budget is not set, Financial Score is null and remaining weights sum to 100%.
FAIL: Score is missing, score is outside valid range, sub-scores do not produce correct weighted average when manually verified.

### AC-SCORE-002: Critical Risk Blocking
PASS: A property in a known flood zone receives a Critical Risk flag that appears above the Family Fit Score on the evaluation report. The flag uses language that is unambiguous ("This property is in a flood zone. Recommend independent flood assessment before proceeding.").
FAIL: Risk flag is missing, buried below the score, or uses ambiguous language.

### AC-REPORT-001: Property Evaluation Report Completeness
PASS: A property evaluation report page contains all required sections: critical risks (if applicable), Family Fit Score with recommendation level, Five-Year Fit Score, Confidence Score, all five sub-score breakdowns with AI explanation text, travel time panel, non-negotiables checklist, strong preferences checklist, and "Day in the Life" narrative.
FAIL: Any required section is missing or displays an error state.

### AC-AI-001: AI Advisor Contextual Awareness
PASS: When a user asks "Which of our shortlisted properties has the best community score?" the AI Advisor returns a correct answer that references actual properties in the shortlist with their real scores. The answer uses the family members' real names.
FAIL: AI returns generic answer, hallucinates properties not in the shortlist, or fails to reference actual data.

### AC-DJ-001: Decision Journal Auto-Creation
PASS: When a user submits a property rating of 4 stars, a Decision Journal entry of type "Reaction" is automatically created within 5 seconds with the timestamp, author, rating, and an AI-generated one-sentence summary of the rating.
FAIL: Entry not created, entry has wrong type, or timestamp is missing.

### AC-NOTIF-001: Daily Brief Email
PASS: A Daily Brief email is received in the registered inbox at the configured time (within ±5 minutes). Email contains top 3 properties with scores, renders correctly in Gmail, and the unsubscribe link functions.
FAIL: Email not received, email contains broken formatting, or unsubscribe link does not work.

### AC-SCHOOL-001: School Intelligence Completeness
PASS: Somerset College and All Saints each have a complete school profile with: School Score, ICSEA value, NAPLAN summary, co-curricular highlights, AI narrative, and a commute time calculated from at least one shortlisted property.
FAIL: Either school profile is incomplete, ICSEA value is missing, or commute time is not displayed.

### AC-SUBURB-001: Suburb Tier Classification
PASS: All target suburbs (minimum 8) have a Tier A/B/C classification with a written rationale of at least 2 sentences. Tier classification is consistent with the family's stated priorities and scoring weights.
FAIL: Any target suburb is unclassified, classification contradicts evident scoring data, or rationale is missing.

---

## 10. Assumptions & Dependencies

### Assumptions

**ASM-001**: The family's budget (BudgetMin/BudgetMax) will be provided during or shortly after onboarding. Until then, Financial Score is disabled. This is a critical data gap.

**ASM-002**: Apify's REA and Domain scraper actors return reliably structured JSON for all required property fields. Apify is a paid service — confirm per-scrape cost and rate limits before build (estimated ~$0.001–0.005 per listing). The development team must confirm the correct Apify actor IDs for realestate.com.au and domain.com.au, and test against 5 real Gold Coast listings before the ingestion sprint begins.

**ASM-003**: ABS 2021 Census data is sufficient for Community Score in MVP. More recent data (ABS 2026 Census, expected release late 2027) is not yet available. Scores should note the data vintage.

**ASM-004**: Google Maps Distance Matrix API will provide accurate travel times for the Gold Coast geography. Gold Coast's road network is well-mapped and results should be reliable.

**ASM-005**: OpenAI GPT-4o is used for qualitative scoring and narrative generation — NOT for structured field extraction (handled by Apify). AI is only invoked for inferring non-structured attributes (e.g., indoor-outdoor flow quality from listing description, modernity assessment from listing language and images).

**ASM-006**: Somerset College is the primary school preference. All Saints is secondary. If neither is suitable, the platform should flag this explicitly rather than defaulting to a third option.

**ASM-007**: The platform is used on desktop as the primary device during MVP. Mobile is secondary and must be usable but need not be pixel-perfect.

**ASM-008**: Clerk's free tier is sufficient for MVP (single family account). Upgrade required at commercialisation.

### External Dependencies

| Dependency | Purpose | Risk Level | Mitigation |
|---|---|---|---|
| OpenAI API (GPT-4o) | Scoring, extraction, advisor, narratives | High | Rate limit monitoring, fallback to GPT-4o-mini for non-critical tasks, Sentry alerts on 5xx |
| Google Maps API | Travel times, POI data | Medium | Cache aggressively, display cached-time warnings to user |
| Clerk | Authentication | Low | Managed service, high reliability |
| Vercel | Frontend hosting | Low | Managed service |
| Railway | Backend + PostgreSQL + Redis | Medium | Monitor Railway status, ensure daily DB backups |
| Resend | Email delivery | Low | Email is a nice-to-have in MVP — failure should not block core functionality |
| realestate.com.au / domain.com.au | Property data source (URL extraction) | High | These platforms may change their HTML structure, breaking extraction. Monitor extraction accuracy; implement alert if >30% null fields |
| ABS Census data | Community Score | Low | Static data, cached locally |
| QPS Crime Statistics | Crime sub-score | Medium | May require manual periodic download and import |
| MySchool / ACARA | School Score data | Low | Public data, accessible via web scrape or manual import |

---

## 11. Risks & Mitigations

### Product Risks

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| Budget not provided, Financial Score always null | High | Medium | Make budget capture mandatory in onboarding with clear explanation of why it matters. Allow "I'll add this later" but display persistent warning. |
| User over-indexes on the score and ignores nuance | Medium | High | Display AI explanation text prominently alongside scores. Score is a signal, not a verdict — use language throughout the UI that reinforces this. |
| Susie doesn't engage with the platform (only Ronnie uses it) | Medium | High | Design for Susie's priorities explicitly. "Day in the Life" narrative and aesthetic-first property cards are for Susie. Phase 2 multi-account feature unlocks full joint usage. |
| Property data changes after extraction (price drop, goes under offer) | High | Medium | Display extraction date prominently. Encourage manual status updates. Phase 2: PropTrack API for live data. |
| Scores feel "black box" and family doesn't trust them | Medium | High | Publish scoring methodology transparently. Allow weight customisation. Show data sources. Let AI explain any score in plain English. |

### Technical Risks

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| realestate.com.au URL extraction breaks (HTML structure change) | High (within 6 months) | High | Build extraction with structured prompt and explicit field-by-field instructions. Add extraction accuracy monitoring. Alert when null field rate spikes. Plan PropTrack API migration for Phase 2. |
| OpenAI API latency causes 30s+ scoring times | Medium | Medium | Stream intermediate results. Show partial scores as they complete. Set user expectation ("Scoring usually takes 20–30 seconds"). |
| Google Maps API cost spikes at scale | Low (MVP, 1 family) | Low | Cache all travel time results per property. Recalculate only when needed. Monitor monthly spend. |
| Data quality of ABS 2021 Census is stale for rapidly changing Gold Coast suburbs | Medium | Medium | Flag data vintage in UI. Note which suburbs have seen significant development since 2021. |
| Prompt injection via user-submitted text (property descriptions, notes) | Low | High | Sanitise all user text before inclusion in prompts. Use role separation in prompts. Monitor for unusual AI outputs. |
| Clerk token expiry causes poor UX during long scoring sessions | Low | Low | Implement silent token refresh. Show re-authentication prompt gracefully if refresh fails. |

---

## 12. Success Metrics

### Primary Metric
**Decision Confidence Score**: At the end of each month, prompt the user: "How confident are you in your current decision direction?" (1–5 scale). Target: 4.0+ by end of Month 2 of active use.

### Product Usage Metrics
- Properties submitted per week (target: 5+ per week during active search period)
- AI Advisor sessions per week (target: 3+ per week)
- Daily Brief open rate (target: 60%+)
- Decision Journal entries created (auto + manual) per property (target: 3+)
- Inspection bookings logged (target: 80%+ of Inspect-tier properties get an inspection logged)

### Quality Metrics
- Property extraction accuracy: % of submitted properties where <3 fields require manual correction (target: 85%+)
- Scoring completion rate: % of submissions where full Family Fit Score is available within 30 seconds (target: 95%+)
- AI Advisor satisfaction: thumbs up/down on responses (target: 80%+ positive)
- Score trust: user survey "Do you trust the Family Fit Score?" (target: 4.0/5 by Month 2)

### Outcome Metric (Long-term)
**The ultimate metric**: Did the family make a better relocation decision than they would have without the platform? This is a lagging metric (12 months post-move) but should be defined now and captured via follow-up survey: "Looking back, do you feel you made the right decision about where to move?" Target: 4.5/5.

---

## 13. Roadmap

### Phase 1 — MVP (Weeks 1–10)

**Goal**: A working, opinionated decision platform for Ronnie and Susie's Gold Coast move.

| Week | Milestone |
|---|---|
| 1–2 | Project setup: Next.js + FastAPI scaffolding, Clerk auth, PostgreSQL schema, Railway deploy, Vercel deploy |
| 2–3 | Family profile + onboarding flow (FR-ONB-001 through FR-ONB-006) |
| 3–4 | Property submission + AI extraction (FR-PROP-001 through FR-PROP-007) |
| 4–6 | Scoring engine: all five sub-scores, Five-Year Fit, Confidence, Risk flags (FR-SCORE-001 through FR-SCORE-013) |
| 5–6 | Dashboard + property feed (FR-DASH-001 through FR-DASH-005) |
| 6–7 | Property Evaluation Report (FR-REPORT-001 through FR-REPORT-005) |
| 7–8 | AI Advisor — function calling, family memory, context injection (FR-AI-001 through FR-AI-006) |
| 7–8 | Decision Journal (FR-DJ-001 through FR-DJ-005) |
| 8–9 | Suburb Intelligence + School Intelligence (FR-SUB-001 through FR-SCH-004) |
| 9 | Preference Learning (FR-PREF-001 through FR-PREF-004) |
| 9–10 | Notifications + Daily Brief + Inspection Tracker (FR-NOTIF-001 through FR-INSP-004) |
| 10 | QA, bug fixes, performance testing, Sentry + PostHog instrumentation |

### Phase 2 — Enhanced Intelligence (Months 3–5)

- PropTrack API integration (replacing URL-paste extraction as primary data source)
- PropTrack API integration (replacing Apify as the primary structured data source at scale)
- Automated property monitoring (daily scan of new listings matching criteria)
- Property alert notifications (price change, sold, new listing in Tier A suburb)
- Development Application (DA) awareness near shortlisted properties
- Expanded suburb coverage (Brisbane, Northern NSW comparison)
- PWA / mobile-responsive upgrade

### Phase 3 — Platform Scale (Months 6–12)

- Multi-family architecture: any family can onboard
- White-label mode for buyer's agents
- Financial modelling: stamp duty calculator, mortgage scenarios, holding cost analysis
- Community data partnerships (local council, ABS live feeds)
- School data partnerships (ACARA direct integration)
- City vs. city relocation comparison mode (e.g., "Should we move to Gold Coast or Northern Beaches?")
- Agent integration: one-click inquiry to buyer's agent with family brief attached

---

## 14. Open Questions

**OQ-001 [CRITICAL]: Budget**  
What is the family's BudgetMin and BudgetMax? Without this, Financial Score is permanently disabled and properties cannot be filtered by affordability. Budget is now captured in the **Family Inputs** section (editable at any time — see FR-ONB-004a). Recommendation: prompt for budget early in onboarding with a clear explanation of why it matters, and allow deferral with a persistent warning banner displayed until it is set.

**OQ-002 [RESOLVED]: Property URL Extraction — Apify Confirmed**  
The extraction approach has been confirmed as **Apify** (apify.com), not raw HTTP fetching. Apify provides purpose-built scrapers for realestate.com.au and domain.com.au that return structured JSON, handling anti-bot protection and JavaScript rendering. An Apify account and API token are required before build. The development team should validate the Apify actor IDs for REA (`apify/realestate-com-au-scraper` or equivalent) and Domain before the property ingestion sprint begins. Action: confirm Apify actor names and test against 5 real Gold Coast listing URLs before build.

**OQ-003 [RESOLVED]: Susie's Account**  
Susie will have her own Clerk account linked to the shared family record. This is now an MVP feature (see FR-ONB-005). The primary user (Ronnie) invites Susie by email. Both see the same family data with individual preference profiles tracked separately. No workaround required.

**OQ-004 [HIGH]: Data Source for Community Score**  
The Community Score relies on ABS 2021 Census data and QPS crime statistics. Who will source, clean, and load this data into the database? Is this a developer task or a product/research task? What format will it be delivered in (CSV, API, manual entry)? This needs an owner before the scoring engine build begins.

**OQ-005 [MEDIUM]: Somerset College vs. All Saints — Primary Preference**  
Is there an already-agreed school preference, or is this genuinely open? The AI recommendation in the School Intelligence module will take a clear position. Understanding whether the family has a lean will help calibrate the recommendation framing.

**OQ-006 [MEDIUM]: Google Maps API Billing**  
Has the Google Maps API key been set up with billing enabled? Distance Matrix API is not free beyond a monthly credit threshold. For a single family in MVP this will likely stay within free tier, but should be confirmed and monitored.

**OQ-007 [MEDIUM]: Flood Risk Data Source**  
Queensland flood risk data is available from the QFlood portal and the Queensland Spatial Catalogue. The data is polygon-based (flood overlay zones). How will this be ingested? Option A: Manual lookup per suburb (not scalable). Option B: Integrate QFlood polygon data and spatial query by property address. Option B is correct but requires PostGIS or a spatial query library. Recommend flagging flood risk as "manual verification required" in MVP and building the spatial query in Phase 2.

**OQ-008 [MEDIUM]: Aircraft Noise Data**  
Gold Coast Airport (OOL) flight path data is available from Airservices Australia. The relevant noise contours (ANEF charts) are publicly available as PDFs with polygon overlays. Same ingestion question as flood data — recommend static polygon for MVP covering known high-noise areas (Bilinga, Tugun, parts of Palm Beach).

**OQ-009 [LOW]: Current City / Origin**  
Where is the family currently located? This affects the "lifestyle improvement" dimension of the Five-Year Fit Score and allows the platform to frame comparisons meaningfully ("vs. your current suburb").

**OQ-010 [LOW]: Move Timeline**  
What is the target move date? This creates urgency signals in the recommendation engine and affects Daily Brief prioritisation (e.g., as move date approaches, inspection urgency increases).

**OQ-011 [LOW]: PostHog vs. Custom Analytics**  
PostHog is listed in the stack for product analytics. Which events should be tracked from day one? Recommend defining a core event taxonomy before build: `property_submitted`, `score_viewed`, `report_opened`, `advisor_session_started`, `advisor_message_sent`, `inspection_logged`, `journal_entry_created`, `daily_brief_opened`. This should be instrumented from the first deploy.

**OQ-012 [LOW]: Mabel's Yard Requirements**  
Is there a minimum yard size or fencing requirement for Mabel? If so, this should be captured as a non-negotiable or strong preference in onboarding and reflected in the Property Score's "block utility" sub-dimension.

---

*Document ends. Next step: engineering kickoff session to walk through Sections 7 (Functional Requirements) and 9 (Acceptance Criteria) with the development team. Assign owners to Open Questions OQ-001 through OQ-004 before build begins.*
