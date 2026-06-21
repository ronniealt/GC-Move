# Gold Coast Move OS — UX Specification
**Version:** 1.0  
**Date:** 2026-06-20  
**Status:** Implementation Grade  

---

## Overview

Gold Coast Move OS is an AI-powered Family Decision Intelligence Platform. It functions as a trusted advisor helping families relocate to the Gold Coast by evaluating properties, suburbs, and schools through the lens of family life outcomes. The product should feel like a calm, confident premium consultant — not a real estate portal.

This document is written for frontend developers and is intended to be complete enough to implement without further design clarification.

---

## 1. Information Architecture

### 1.1 Sitemap

```
/ (Landing / Login)
/onboarding
  /onboarding/family-basics       (Step 1)
  /onboarding/members             (Step 2)
  /onboarding/non-negotiables     (Step 3)
  /onboarding/schools             (Step 4)
  /onboarding/review              (Step 5)
/dashboard
/properties
  /properties/submit              (Paste URL)
  /properties/[id]/processing     (AI extraction in progress)
  /properties/[id]                (Evaluation Report)
  /properties/compare             (Side-by-side comparison)
/advisor                          (AI Chat)
/journal
  /journal/[id]                   (Individual journal entry)
/suburbs
  /suburbs/[slug]                 (Suburb detail page)
/schools                          (School comparison)
/shortlist
/inspections
/preferences
/settings
  /settings/profile
  /settings/notifications
```

### 1.2 Primary Navigation

The main navigation is a persistent left sidebar on desktop (collapses to a bottom tab bar on mobile). Navigation items in order:

1. Dashboard (home icon)
2. Properties (building icon) — includes Submit, Shortlist sub-items
3. Advisor (chat bubble icon) — AI chat
4. Suburbs (map pin icon)
5. Schools (graduation cap icon)
6. Inspections (calendar icon)
7. Journal (book icon)
8. Preferences (sliders icon)
9. Settings (gear icon, bottom of sidebar)

### 1.3 URL Structure

All authenticated routes sit under a clean path hierarchy. Route parameters use kebab-case slugs (e.g., `/suburbs/broadbeach-waters`). Property IDs are UUIDs. The dashboard is the default redirect after login for returning users. Onboarding is the default redirect for new users who have not completed profile setup.

---

## 2. User Flows

### 2.1 Onboarding Flow (New Family Setup)

**Trigger:** User signs up via Clerk auth (email or Google). Clerk redirects to `/onboarding/family-basics`.

**Step 1 — Family Basics** (`/onboarding/family-basics`)  
User enters: family surname, current city/state, target move date (month/year picker), total budget (slider + manual input), preferred budget (lower bound). User clicks "Continue".

**Step 2 — Family Members** (`/onboarding/members`)  
User adds each family member. A pre-populated card is shown for "Add a person" and "Add a pet". For each person: name, age, role (Parent / Child / Other), and up to 5 priority tags from a tag library (e.g., "Beach access", "School quality", "Walkability", "Community feel", "Modern kitchen", "Home office", "Yard space"). For pets: name, breed, and relevant tags (Yard, Parks nearby, Dog beach). Minimum 1 adult required to continue.

**Step 3 — Property Non-Negotiables** (`/onboarding/non-negotiables`)  
Checklist UI. User selects hard requirements from a curated list: minimum bedrooms (1–6+ stepper), minimum bathrooms (1–4+), garage (yes/no/don't care), pool (yes/no/don't care), minimum land size (dropdown: any / 300m2 / 500m2 / 800m2+), flood zone (must exclude / acceptable), dual living (yes/no/don't care). A free-text field allows adding custom non-negotiables.

**Step 4 — School Preferences** (`/onboarding/schools`)  
User selects school type preferences: Independent / Catholic / State. Multi-select suburb rings for school catchment priority. Pre-populated option cards for Somerset College and All Saints Anglican School with brief descriptions. User can select "Currently considering", "Already decided", or "Not relevant". Year level(s) entry for any children.

**Step 5 — Review & Confirm** (`/onboarding/review`)  
Full summary of all entries in card form. Each section has an "Edit" link that returns the user to that step without losing other data. A prominent "Start Exploring" primary button completes onboarding and redirects to `/dashboard`.

**Progress Indicator:** A 5-step progress bar is shown at the top of all onboarding screens. Steps are labelled (Basics, Members, Requirements, Schools, Review). Completed steps show a filled indicator. Current step is highlighted in teal. Steps are not clickable (linear flow only).

**Back Navigation:** Each step has a "Back" text link that navigates to the previous step, preserving entered data.

---

### 2.2 Property Submission Flow

**Trigger:** User clicks "Add Property" in the sidebar or the dashboard CTA.

1. User lands on `/properties/submit`. A large text area is shown with placeholder "Paste a property listing URL — realestate.com.au, Domain, or any agent website".
2. User pastes URL and clicks "Analyse Property".
3. System validates URL format (client-side). If invalid, inline error shown without page navigation.
4. If valid, redirect to `/properties/[id]/processing`. A new property record is created with status `processing`.
5. Processing screen shows animated progress: "Fetching listing", "Extracting property details", "Analysing suburb", "Evaluating school catchment", "Generating family report". Each step checks off as complete.
6. On completion, redirect to `/properties/[id]`.
7. On failure (scrape fails or AI error), redirect to `/properties/submit` with an error banner. User is offered to enter details manually via a "Enter manually" secondary button.

**Manual Entry Fallback:** A structured form with fields: address, price, bedrooms, bathrooms, garage, land size, property type, listing description (free text), image URL (optional). Submitting this triggers the same AI evaluation pipeline.

---

### 2.3 Property Evaluation Review Flow

1. User arrives at `/properties/[id]` after processing, or by clicking a property from the shortlist or dashboard.
2. Page loads with Family Fit Score animating in (count-up from 0 over 1.2 seconds).
3. User reads the AI recommendation summary at the top.
4. User scrolls through category scores, per-person impact cards, risk flags, suburb context, school summary.
5. User can "Save to Shortlist" (heart icon button, top right of page). Toast confirmation appears.
6. User can open the AI Advisor pre-seeded with this property context via "Discuss with Advisor" button.
7. User can add a note to the Decision Journal via "Add to Journal" button, which opens a modal with a text area.
8. User can mark inspection status: "Schedule Inspection" opens the Inspection Tracker modal.

---

### 2.4 AI Advisor Conversation Flow

1. User navigates to `/advisor` or opens a pre-seeded conversation from a property page.
2. If no prior conversation, an empty state with 3–4 suggested prompt chips is shown.
3. User types a message or selects a prompt chip.
4. Assistant response streams in with typing indicator visible during generation.
5. If the conversation references a specific property or suburb, a Property Card or Suburb Card is embedded inline in the response.
6. If the AI detects a new preference signal ("I really prefer double garages"), a Preference Capture Toast appears at the bottom right: "I've noted your preference for double garages. Want me to update your profile?" with Confirm / Dismiss actions.
7. Conversation persists across sessions. A conversation history sidebar (desktop) or accordion (mobile) shows prior conversation threads by date.

---

### 2.5 Decision Journal Flow

1. Entries are created automatically when: a property evaluation is completed, user adds a manual note, or a property is moved to a shortlist/rejected state.
2. User visits `/journal` to see all entries in reverse chronological order.
3. Each entry shows: date, property address (if applicable), entry type badge, and a text excerpt.
4. Clicking an entry navigates to `/journal/[id]` which shows the full entry, linked property evaluation (if applicable), and any manual notes.
5. User can add a note to any entry inline with a text field.
6. User can export journal as PDF (future — shown greyed out in MVP with "Coming soon" tooltip).

---

### 2.6 Inspection Booking Flow

1. Triggered from Property Evaluation page or Inspection Tracker.
2. Modal opens: inspection date (date picker), time (time input), agent name (text), agent phone (text), notes (text area).
3. Saving creates an entry in `/inspections`.
4. Inspection Tracker shows upcoming and past inspections in a calendar list view.
5. Post-inspection: User can add notes and rate the property (prompted with "How did it feel?" 1–5 stars, plus free text).

---

### 2.7 Shortlist Comparison Flow

1. User visits `/shortlist`. All saved properties are shown as Property Cards.
2. User selects 2–3 properties via checkboxes that appear on card hover/tap.
3. "Compare Selected" button appears in a sticky action bar at the bottom of the screen.
4. Clicking navigates to `/properties/compare?ids=[id1],[id2],[id3]`.
5. Comparison shows side-by-side columns for each property. Rows: Family Fit Score, Category Scores (5 rows), Bedrooms/Bathrooms/Land, Price, Suburb, School Catchment, AI Recommendation, Key Risks.
6. The highest score in each row is highlighted in green.
7. A "Best overall for your family" summary at the top recommends one property based on composite score.

---

## 3. Screen Specifications

### 3.1 Landing / Login Page — `/`

**Purpose:** First impression. Authenticate returning users, explain value to new visitors.

**Layout:** Full-bleed hero, no sidebar. Clerk authentication modal used for sign in/up.

**Components:**
- Navigation bar: Logo (top left), "Sign In" (top right, ghost button), "Get Started" (primary button).
- Hero section: Headline "Find the Gold Coast life that fits your family." Subheadline "AI-powered family decision intelligence — not just a property search." Two CTAs: "Get Started Free" (primary) and "See how it works" (ghost, scrolls to features section).
- Features row (3 columns): "Evaluate every property through your family's lens", "Suburb intelligence built for real life", "An AI advisor who knows your family".
- Social proof strip: Simple text quote from a fictional family (placeholder for testimonials). 
- Footer: minimal — logo, privacy policy link, contact email.

**Empty/Error States:** Clerk handles auth errors natively. No custom states required here.

**Mobile:** Hero text scales down. Feature columns stack vertically. CTAs are full-width.

---

### 3.2 Onboarding Step 1: Family Basics — `/onboarding/family-basics`

**Layout:** Centred card layout, max-width 560px, no sidebar. Progress bar at top.

**Components:**
- Progress bar (5 steps, step 1 active).
- Page title: "Let's start with the basics".
- Form fields:
  - Family name (text input, placeholder "e.g. Altit Family").
  - Current city/state (text input with autocomplete).
  - Target move date (month/year picker, shows 12-month rolling options from current date).
  - Total budget: dual-thumb range slider from $500k to $5M, step $50k. Current value shown in large type between the thumbs. Manual input fields below the slider for exact entry.
  - Preferred budget (single thumb, must be ≤ total budget, validated on blur).
- Continue button (primary, full width on mobile, right-aligned on desktop).

**Validation:** All fields required. Budget validation: preferred must be less than total. Error messages appear below each field in muted red.

**Mobile:** Single column, full-width inputs.

---

### 3.3 Onboarding Step 2: Family Members — `/onboarding/members`

**Layout:** Centred, max-width 640px. Progress bar step 2.

**Components:**
- Page title: "Who's making the move?"
- Member cards displayed in a responsive grid (2 columns desktop, 1 column mobile).
- Each member card contains: Name (text input), Age (number input, optional for adults), Role selector (Parent / Child / Other / Pet — segmented control), Priority tag picker (tag cloud of ~20 options, up to 5 selectable, selected tags shown in teal chip style).
- "Add person" button (dashed border card with + icon).
- "Add pet" button (same style, renders a pet-specific card with Name, Pet type, and relevant tags).
- Continue button.

**Pre-populated state:** If user is Ronnie (detected via auth email), the system pre-populates Ronnie (55, Parent), Susie (45, Parent), Austin (7, Child), and Mabel (Groodle, Pet) as a suggested starting point with a banner "We've set up a suggested family profile — edit or add as needed."

**Validation:** At least one adult (Parent role) required. Each member requires a name.

---

### 3.4 Onboarding Step 3: Property Non-Negotiables — `/onboarding/non-negotiables`

**Layout:** Centred, max-width 560px. Progress bar step 3.

**Components:**
- Page title: "What are your must-haves?"
- Subtitle: "These are hard requirements. Properties that don't meet them will be flagged."
- Stepper controls for: Minimum bedrooms (1–6+), Minimum bathrooms (1–4+).
- Toggle groups for: Garage (Must have / Nice to have / Don't care), Pool (same), Dual living (same).
- Dropdown for minimum land size (Any / 300m2+ / 500m2+ / 800m2+).
- Flood zone toggle: "Exclude flood zone properties" (on by default).
- Free text field: "Anything else?" (optional, max 200 chars).
- Continue button.

---

### 3.5 Onboarding Step 4: School Preferences — `/onboarding/schools`

**Layout:** Centred, max-width 560px. Progress bar step 4.

**Components:**
- Page title: "Tell us about schools."
- School type multi-select: Independent / Catholic / State (pill buttons, multi-select).
- Pre-built school cards for Somerset College and All Saints Anglican School. Each card shows: school name, type, year levels, suburb. Status selector: "Considering" / "Decided" / "Not relevant".
- "Add another school" text button opens a search field.
- Year levels input: for each child member, a year level selector (Pre-Prep through Year 12).
- Continue button.

---

### 3.6 Onboarding Step 5: Review & Confirm — `/onboarding/review`

**Layout:** Centred, max-width 640px. Progress bar step 5.

**Components:**
- Page title: "Here's your family profile."
- Summary card for each section: Family Basics, Members, Requirements, Schools. Each section card has an "Edit" link (right aligned) that navigates back to that step.
- Members are displayed as avatar-initial chips with name and role label.
- A warm blue info banner: "Gold Coast Move OS will use this to personalise every evaluation, suburb rating, and recommendation for your family."
- "Start Exploring" button (primary, prominent).

---

### 3.7 Dashboard — `/dashboard`

**Purpose:** Daily command centre. Shows what's new, what the AI recommends, and quick access to all core functions.

**Layout:** Left sidebar (fixed, 240px) + main content area. Top bar with family name and avatar.

**Main content sections (top to bottom):**

**Daily Brief (top section):**  
A card with the AI-generated daily brief. Heading: "Morning, [Family Name]". Subheading: "Here's what matters today — [date]". Body: 2–3 sentences of natural-language insight (e.g., "Two new listings in your target suburbs appeared overnight. Broadbeach Waters continues to look like your strongest suburb match. Your next inspection is Saturday at 10am."). "Read more" expands the brief inline.

**Top Recommendations (below Daily Brief):**  
Horizontal scrollable row of PropertyCard components (3 visible on desktop, 1.2 visible on mobile to hint scroll). Heading: "Properties to look at today". Each card includes the RecommendationBadge.

**Suburb Intelligence Snapshot (below Recommendations):**  
A row of 3 SuburbCard components for the user's top-matched suburbs. Heading: "Your top suburbs".

**Shortlist Activity (below Suburb Intelligence):**  
If shortlist has items: shows last 3 shortlisted properties with most recent activity timestamp. If empty: empty state card (see below).

**Recent Journal Entries:**  
Last 2 journal entries as JournalEntryCard components.

**Upcoming Inspections:**  
If any scheduled: shows next 2 inspections with date/time and property address. If none: CTA to schedule first inspection.

**Empty State (new user, no properties submitted):**  
Full-width banner card: "Add your first property to get started. Paste a listing URL and we'll evaluate it for your family." with "Add Property" button.

**Loading State:**  
Skeleton loaders for each card section. Cards shimmer with a left-to-right animation. Daily brief loads first, then recommendations.

**Mobile:** Sidebar collapses to bottom tab bar (5 icons: Dashboard, Properties, Advisor, Suburbs, More). Main content stacks vertically. Horizontal scroll rows maintained.

---

### 3.8 Property Submission — `/properties/submit`

**Layout:** Centred, max-width 640px. Sidebar visible.

**Components:**
- Page title: "Add a property to evaluate."
- Large URL text area (3 rows minimum), placeholder: "Paste a listing URL from realestate.com.au, Domain, or any agent website."
- "Analyse Property" button (primary, full width).
- Divider with "or" text.
- "Enter details manually" secondary button (ghost style, opens inline form below).
- Tip text: "We support realestate.com.au, domain.com.au, and most Gold Coast agency websites."

**Manual Entry Form (hidden by default, revealed on secondary button click):**  
Fields: Address (text), Price (number, formatted as currency), Property type (House / Townhouse / Apartment / Land — radio), Bedrooms (stepper), Bathrooms (stepper), Garage spaces (stepper), Land size m2 (number), Listing description (textarea), Image URL (text, optional). Submit button: "Evaluate This Property".

**Validation:** URL must be non-empty and match http/https pattern. Address required for manual entry. Error states: red border + message below field.

**Error State:** If AI extraction fails, a red banner appears: "We couldn't extract this listing. This sometimes happens with non-standard pages." with the manual entry form expanded automatically.

---

### 3.9 Property Processing — `/properties/[id]/processing`

**Layout:** Centred, max-width 480px. No sidebar (immersive focus).

**Components:**
- Property address shown at top (if available from initial extraction).
- Animated progress indicator: vertical list of steps, each with an icon and label. Steps:
  1. Fetching listing details
  2. Extracting property features
  3. Analysing suburb and location
  4. Evaluating school catchment
  5. Generating family evaluation report
- Each step transitions: pending (grey circle) → active (spinning teal ring) → complete (green checkmark).
- Estimated time text: "This usually takes 20–40 seconds."
- A rotating quote/tip panel at the bottom: cycling through 3 short tips about the family's profile (e.g., "We're checking Somerset College's catchment zone for Austin.").

**Error State:** If processing exceeds 90 seconds without completion, an error state replaces the progress indicator: "This is taking longer than expected." with two options: "Keep waiting" and "Try again". If backend returns an error, a more specific message is shown with a link back to `/properties/submit`.

**No Mobile Special Case:** This screen is the same on mobile and desktop. Vertically centred.

---

### 3.10 Property Evaluation Report — `/properties/[id]`

**Purpose:** The core value screen. Complete AI-generated assessment of a property for the family.

**Layout:** Sidebar + main content. Main content is a single long-scroll page with sticky top bar showing the property address and key action buttons.

**Sticky Top Bar (appears on scroll):**  
Property address (truncated), Family Fit Score badge (small), "Save to Shortlist" icon button, "Discuss with Advisor" icon button, "Add to Journal" icon button.

**Page Sections (in order):**

**Hero Section:**  
Property image (full width, max height 400px, object-fit cover). If no image: illustrated placeholder with teal gradient. Over the image (bottom left): address, suburb, price. Top right overlay: RecommendationBadge.

**Family Fit Score Panel:**  
Large centred display. The FamilyFitScoreCard component. Score animates in on page load (1.2 second count-up). Below the score: 1–2 sentence AI recommendation summary in italic quote style.

**Category Scores Row:**  
CategoryScoreRow component showing 5 scores: Community (0–10), Lifestyle (0–10), Schools (0–10), Property (0–10), Financial (0–10). Each with a ring/gauge and colour coding.

**Property Snapshot:**  
2-column grid (1 column mobile): Bedrooms, Bathrooms, Garage, Land size, Property type, Year built (if known), Listed price, AI estimated value (with ConfidenceIndicator). Address link to Google Maps.

**Per-Person Impact (Family Lens):**  
Horizontal scrollable row of FamilyMemberImpactCard components — one for each family member. Each card shows member name, avatar initial, a brief 2–3 sentence commentary, and a personal fit score (0–10) with colour-coded ring.

**Risk Flags:**  
Section heading: "Things to be aware of." RiskFlag components displayed in a 2-column grid. If no risks: a muted green "No major risks identified for this property" message.

**Suburb Context:**  
Summary of the suburb: tier classification (Premium / Good / Acceptable / Below Target), suburb score, 3 key lifestyle attributes, school catchment summary, drive time to beach, drive time to Somerset College.

**School Catchment:**  
For each school the family is interested in: name, type, whether the property is in catchment (yes/no badge), AI commentary on fit for Austin's year level.

**AI Insights (Full):**  
The complete AI evaluation narrative, broken into collapsible sections: "Why this property scores well", "Concerns and considerations", "How this fits your family's priorities", "Our recommendation". Each section uses an accordion (collapsed by default to avoid overwhelming scroll).

**Action Bar (bottom of page):**  
Three full-width stacked buttons (mobile) or row (desktop): "Save to Shortlist" (primary), "Discuss with Advisor" (secondary), "Add to Journal" (ghost).

**Loading State:** All sections load with skeleton shimmer. The Family Fit Score section shows a spinning ring placeholder. Content populates from top to bottom as the AI response streams in.

**Mobile:** Hero image full width, 250px height. Scores stack vertically. Per-person impact cards scroll horizontally. Action buttons are fixed to the bottom of the viewport.

---

### 3.11 AI Advisor — `/advisor`

**Layout:** Split: conversation thread (main) + context panel (right sidebar, 280px, desktop only).

**Context Panel (desktop):**  
Shows current family context: member chips, active shortlist count, properties discussed in this session.

**Conversation Area:**  
Messages in chronological order. User messages: right-aligned, dark background. AI messages: left-aligned, white card with teal left border. Typing indicator: three dots animated.

**Inline Property/Suburb Cards:** When the AI references a property or suburb, a compact card is embedded in the message bubble. Clicking the card navigates to that resource.

**Input Area (bottom, fixed):**  
Text input (multiline, max 4 rows). Send button (right). Character limit indicator at 1000 chars. Below input: "Shift+Enter for new line, Enter to send."

**Suggested Prompts (empty state):**  
4 chips: "Which suburb suits us best?", "Compare Broadbeach Waters and Mermaid Waters for us", "What should we look for when inspecting on Saturday?", "How does [most recent property] compare to our ideal?"

**Preference Capture Toast:**  
Appears at bottom-right corner. White card, teal accent, 3-second auto-dismiss if no action. Contains: "I noticed you mentioned [preference]. Add this to your profile?" with "Yes, save it" and "No thanks" buttons. Dismissing with "Yes" triggers a confirmation animation (checkmark appears briefly).

**Mobile:** Context panel hidden. Full-screen conversation. Input fixed to bottom of viewport.

---

### 3.12 Decision Journal — `/journal`

**Layout:** Sidebar + main content. Two-column layout on desktop: entry list (left, 360px) + entry detail (right). Single column on mobile.

**Entry List:**  
Reverse chronological. Each JournalEntryCard shows: date, property address or "General note", entry type badge (Evaluated / Inspected / Rejected / Note), first line of content.

**Entry Detail:**  
On click of a card: detail loads in right panel (desktop) or navigates to `/journal/[id]` (mobile). Shows: full AI entry or user note, linked PropertyCard if applicable, timestamp, "Add note" inline text field at bottom.

**Filters:**  
Horizontal filter chips at top of list: All / Evaluations / Inspections / Notes. Selecting a filter updates the list instantly.

**Empty State:**  
"Your decision journal is empty. Evaluate a property to create your first entry." with "Add Property" button.

---

### 3.13 Suburb Intelligence — `/suburbs` and `/suburbs/[slug]`

**List View (`/suburbs`):**  
Grid of SuburbCard components. Top of page: filter bar with Tier filter (Premium / Good / Acceptable / All), sort by (Family Fit / Price / Beach Distance / School Score). Heading: "Gold Coast Suburbs for Your Family."

Each SuburbCard: suburb name, tier badge, family fit score (large), 3 key attribute tags, beach distance, median price.

**Suburb Detail Page (`/suburbs/[slug]`):**  
Sections: Hero (suburb name, tier badge, hero image), Suburb Score Panel (equivalent to FamilyFitScoreCard but suburb-focused), Category Scores Row (Community / Lifestyle / Schools / Property / Financial), Lifestyle Attributes (tag grid), School Catchment (schools in this suburb), Properties in shortlist from this suburb (if any), AI Commentary (narrative on suburb fit for the family), Nearby Suburbs (3 SuburbCard components for adjacent suburbs).

---

### 3.14 School Intelligence — `/schools`

**Layout:** Sidebar + full-width main content.

**Components:**
- Page heading: "Schools on the Gold Coast."
- Filter bar: Type (Independent / Catholic / State), Year level (dropdown), Suburb (multi-select).
- School comparison table: rows = schools, columns = Name / Type / Year Levels / Suburb / Catchment Match / AI Fit Score / ATAR / Details link.
- Clicking a school row expands an inline accordion showing: AI commentary for the family, Austin's fit (age/year level relevant), Ethos and culture notes, Distance from target suburbs, Application process note.
- Two featured SchoolCard components pinned at top: Somerset College and All Saints Anglican School, each with a "Family fit" badge.

---

### 3.15 Shortlist — `/shortlist`

**Layout:** Sidebar + main content grid.

**Components:**
- Page heading: "Your Shortlist" with property count badge.
- Sort controls: Family Fit Score (default) / Date Added / Price.
- Grid of PropertyCard components (3 columns desktop, 2 tablet, 1 mobile).
- Each card has a checkbox (visible on hover/tap) for comparison selection.
- "Compare Selected (N)" sticky button at bottom when 2+ properties checked.
- Empty state: "No saved properties yet. Start evaluating properties to build your shortlist." with "Add Property" CTA.

---

### 3.16 Property Comparison — `/properties/compare`

**Layout:** Full-width. No sidebar during comparison (more horizontal space needed).

**Structure:** 3-column table (one per property). Sticky first column with row labels. Scrollable property columns.

**Rows:** Property image + address (header), Family Fit Score, Community Score, Lifestyle Score, Schools Score, Property Score, Financial Score, Price, Bedrooms, Bathrooms, Land size, Suburb tier, School catchment match, AI Recommendation summary, Key risks.

**Visual Treatments:** Highest score in each numeric row: green background. Lowest score: muted red background. Equal values: no colour.

**Header Summary:** "Best overall match for your family: [Property Address]" in a teal banner at the top. Back button to shortlist.

---

### 3.17 Inspection Tracker — `/inspections`

**Layout:** Sidebar + main content. Two tabs: Upcoming / Past.

**Upcoming tab:**  
Chronological list of scheduled inspections. Each row: date/time, property address, agent name, agent phone, notes preview. "Add notes" and "Mark as done" inline actions.

**Past tab:**  
Completed inspections. Each shows: post-inspection rating (1–5 stars), notes, link to property evaluation.

**Add Inspection Modal:**  
Triggered from Property Evaluation page or "Schedule Inspection" button on this page. Fields: Property (search/select or type address), Date, Time, Agent name, Agent phone, Notes. Save button.

**Empty State (Upcoming):** "No inspections scheduled. Head to a property page to schedule one." with "Browse Shortlist" link.

---

### 3.18 Preference Profile — `/preferences`

**Purpose:** Show what the AI has learned about the family's preferences over time.

**Layout:** Sidebar + main content.

**Sections:**

**Preference Summary:**  
Horizontal bar chart showing relative weighting of priorities: Community / Lifestyle / Schools / Property Features / Financials. These weights are derived from AI interaction history.

**Learned Preferences (per person):**  
Expandable section for each family member. Shows PreferenceTag chips — tags the AI has inferred from chat conversations, property reactions, and onboarding data. Tags have a confidence indicator (High / Medium / Inferred). Each tag has an X to remove and a "confirm" checkmark if not yet confirmed.

**Non-negotiables Summary:**  
Display of current hard requirements from onboarding, with "Edit" link to settings.

**Preference History:**  
Timeline of when preferences were captured, the source (Chat / Evaluation / Onboarding), and the preference text.

**Empty/Early State:**  
If fewer than 3 evaluations have been done: "Your preference profile is just getting started. As you evaluate properties and chat with your advisor, we'll build a detailed picture of what matters to your family."

---

### 3.19 Settings — `/settings/profile` and `/settings/notifications`

**Profile Settings (`/settings/profile`):**  
Edit all onboarding data. Section tabs: Family Basics / Members / Requirements / Schools. Each section renders the same form as the corresponding onboarding step. "Save Changes" button per section.

**Notification Settings (`/settings/notifications`):**  
Toggle controls for:
- Daily brief email (on/off, time of day selector)
- New matching property alert (on/off)
- Inspection reminder (24hr before, on/off)
- Preference update digest (weekly, on/off)

Email shown at top (non-editable, managed by Clerk). "Save" button.

---

## 4. Component Specifications

### FamilyFitScoreCard
- Props: `score` (0–100), `label` (optional string), `size` ("sm" | "md" | "lg")
- Display: Circular ring gauge, score as large number in centre, "/ 100" in smaller text below
- Colour: score 90+ = `#6BAE75`, 80–89 = `#4A9B8E`, 70–79 = `#F59E0B`, below 70 = `#DC2626`
- Animation: On mount, ring draws clockwise from 0 to score value over 1.2s (CSS animation), number counts up simultaneously
- Ring width: 8px (lg), 6px (md), 4px (sm). Ring background: `#E8DCC8`. Ring foreground: colour per score
- Label (if provided) appears below the score in `text-sm text-muted-foreground`

### CategoryScoreRow
- Props: `scores` (object: { community, lifestyle, schools, property, financial } all 0–10)
- Display: 5 mini-score rings in a horizontal row, each with label below
- Colour: 8+ = green, 6–7.9 = amber, below 6 = red
- On mobile: wraps to 2+3 or scrolls horizontally
- Each score ring is 48px diameter (sm FamilyFitScoreCard scaled to 0–10)

### RecommendationBadge
- Props: `type` ("Prioritise" | "Inspect" | "Monitor" | "Ignore")
- Display: Pill badge with icon + text
- Styles: Prioritise = green bg, Inspect = teal bg, Monitor = amber bg, Ignore = grey bg
- Icons: Prioritise = star, Inspect = eye, Monitor = clock, Ignore = x-circle

### ConfidenceIndicator
- Props: `level` ("High" | "Medium" | "Low"), `tooltip` (string)
- Display: Small horizontal bar (3 segments), filled according to level (3/3, 2/3, 1/3). Colour: filled = teal, empty = grey.
- On hover: tooltip shows the reason for confidence level
- Sits inline next to any estimated or AI-generated value

### FamilyMemberImpactCard
- Props: `member` ({ name, role, avatar_initial }), `score` (0–10), `commentary` (string)
- Display: White card, 200px wide (horizontal scroll container), member initial avatar (40px circle, teal background), name + role below, personal fit score ring (sm), commentary text (2–3 lines, clamped with "Read more" expand)
- Card has subtle shadow, 8px border-radius

### RiskFlag
- Props: `type` (string, e.g. "Flood Zone"), `severity` ("High" | "Medium" | "Low"), `description` (string)
- Display: Card with coloured left border (High = red, Medium = amber, Low = grey), risk type in bold, description in body text, severity badge in top right
- Expandable: clicking card toggles expanded description

### PropertyCard
- Props: `property` (full property object), `variant` ("feed" | "compact" | "shortlist")
- Display: Image (aspect ratio 16:9), RecommendationBadge overlay (top right), address, suburb, price, FamilyFitScoreCard (sm), 3 attribute chips (beds/baths/land)
- On hover (desktop): subtle card lift (box-shadow + translateY(-2px) transition)
- Save button: heart icon, top left of image. Filled heart = saved, outline = unsaved. Toggle with animation (scale pulse on save)
- "Feed" variant: wider card with 1-line AI summary below attributes
- "Compact" variant: horizontal layout for sidebar/list use

### SuburbCard
- Props: `suburb` (suburb object), `tier` ("Premium" | "Good" | "Acceptable" | "Below Target")
- Display: Image or illustrated gradient header, suburb name, tier badge (coloured), family fit score, 3 attribute tags, median price, beach distance
- Tier badge colours: Premium = teal, Good = green, Acceptable = amber, Below Target = red

### SchoolCard
- Props: `school` (school object), `status` ("Considering" | "Decided" | "Not relevant")
- Display: School name, type badge, year levels, suburb, family fit score, status indicator

### JournalEntryCard
- Props: `entry` (journal entry object)
- Display: Date (relative: "2 days ago"), type badge, address or "General note", text excerpt (1 line, ellipsis), clickable whole card

### PreferenceTag
- Props: `tag` (string), `confidence` ("High" | "Medium" | "Inferred"), `confirmed` (bool), `onRemove`, `onConfirm`
- Display: Pill chip, teal for confirmed, grey for inferred. Confidence dot (filled/half/outline). X button and check button appear on hover

### AIAdvisorMessage
- Props: `role` ("user" | "assistant"), `content` (string | ReactNode), `timestamp`
- User message: right-aligned, `#1A3C5E` background, white text, 8px border-radius, no avatar
- Assistant message: left-aligned, white card, `#4A9B8E` 3px left border, near-black text, timestamp below in muted-sm
- Inline card embeds render inside the assistant message bubble with a slightly inset white-on-white card style

---

## 5. Micro-interactions & States

### Score Animation on First Load
Trigger: Component mounts with a `score` prop.  
Behaviour: Ring stroke-dashoffset animates from full (empty ring) to final value. Number counts up from 0. Duration: 1200ms. Easing: `ease-out`. Uses CSS `@keyframes` for the ring and a `requestAnimationFrame` loop for the counter. Only plays on first mount (not on re-render). If `prefers-reduced-motion` is set, skip animation and show final value immediately.

### Recommendation Reveal
Trigger: Property evaluation page loads.  
Behaviour: RecommendationBadge slides in from the right on the hero image, 300ms, `ease-out`. Delay: 400ms after page load (after score animation begins).

### Save / Unsave Property Animation
Trigger: User clicks heart icon on PropertyCard.  
Behaviour: Heart icon scales up to 1.3x then returns to 1.0x over 300ms. Colour transitions from outline to filled (or vice versa). A brief toast appears: "Saved to shortlist" or "Removed from shortlist" (bottom right, 2-second auto-dismiss, green for save, neutral for remove).

### Preference Capture Toast
Trigger: AI Advisor detects a preference signal in user message.  
Behaviour: Toast slides in from bottom-right, white card with teal accent, shadow. Remains until actioned or 8 seconds. "Yes, save it" triggers: toast content transitions to a checkmark icon + "Got it" and auto-dismisses after 1 second. "No thanks" dismisses immediately.

### Navigation Active State
Trigger: User navigates to a route.  
Behaviour: The corresponding sidebar item's text colour changes to `#1A3C5E` (primary), background changes to `#E8DCC8` (sand), left border of 3px solid `#4A9B8E` (teal) appears. Transition: 150ms ease.

---

## 6. Accessibility Requirements

### Keyboard Navigation
- All interactive elements must be focusable via Tab in logical DOM order.
- Custom components (cards, score rings, tag chips) must have `tabIndex={0}` and respond to Enter/Space for activation.
- Modal dialogs (inspection booking, journal note, confirmation) must trap focus within the modal while open and return focus to the trigger element on close.
- The sidebar navigation must support arrow keys for moving between items.
- Dropdown menus and comboboxes use shadcn/ui primitives which implement ARIA combobox pattern natively.

### ARIA Labels
- All icon buttons must have `aria-label` (e.g., `aria-label="Save to shortlist"`).
- Score rings must have `aria-label="Family Fit Score: 87 out of 100"`.
- Progress bars must use `role="progressbar"` with `aria-valuenow`, `aria-valuemin`, `aria-valuemax`.
- Risk flags: `role="alert"` if severity is High, otherwise standard landmark.
- AI Advisor chat: conversation container has `role="log"` and `aria-live="polite"` so new messages are announced by screen readers.
- RecommendationBadge: `aria-label="Recommendation: Prioritise"`.

### Colour Contrast
- All body text on white backgrounds: minimum 4.5:1 ratio (WCAG AA).
- Primary blue `#1A3C5E` on white `#FAFAF8`: verified pass.
- Teal `#4A9B8E` is used decoratively (borders, accents), not as the sole carrier of information. Text labels always accompany colour-coded scores.
- Warning amber `#F59E0B` on white: used with text label, not colour alone, to ensure accessibility for colour-blind users.
- Danger red `#DC2626` on white: passes AA for normal text.

### Screen Reader Compatibility
- Next.js `<Link>` components include meaningful link text (no "click here").
- Images use descriptive `alt` text. Property images: `alt="[Address] — [suburb] property photo"`. Suburb images: `alt="[Suburb name] suburb"`.
- Skeleton loaders include `aria-busy="true"` on their containers and `aria-label="Loading..."`.
- Score animations are purely visual; the final static value is the accessible value.
- Dynamic route changes announce page titles via a `role="status"` live region that updates on navigation (next.js app router compatible).

---

## 7. Responsive Breakpoints

### Breakpoint Definitions
- **Mobile:** < 768px
- **Tablet:** 768px–1024px
- **Desktop:** > 1024px

### Layout Changes by Breakpoint

**Sidebar Navigation:**  
Desktop: Fixed left sidebar, 240px wide, always visible.  
Tablet: Collapsible sidebar (hamburger toggle in top bar), slides over content, 280px wide, closes on outside click.  
Mobile: Hidden. Replaced by bottom tab bar (5 icon tabs: Dashboard / Properties / Advisor / Suburbs / More).

**Dashboard:**  
Desktop: Full layout as specified.  
Tablet: 2-column card grids, horizontal scroll rows maintained.  
Mobile: Single column. All card grids stack. Horizontal scroll rows maintained (cards at 85vw width).

**Property Evaluation Report:**  
Desktop: Category scores in single row (5 across). Per-person cards in horizontal row.  
Tablet: Category scores in 3+2 wrap. Per-person cards horizontal scroll.  
Mobile: Category scores stack vertically (2 per row). Per-person cards horizontal scroll at 75vw per card. Sticky action bar at bottom of viewport.

**Property Comparison:**  
Desktop: Full 3-column side-by-side.  
Tablet: 2-column (select which 2 to compare, third accessible via toggle).  
Mobile: Single property column with swipe gesture to navigate between selected properties. Row labels stick to left.

**AI Advisor:**  
Desktop: Conversation + right context panel.  
Tablet: Conversation full width, context panel accessible via collapsible drawer.  
Mobile: Full-screen conversation. Context hidden. Input fixed to bottom.

**Onboarding:**  
All steps: Centred card layout, full-width inputs on mobile, comfortable padding on all sizes. Progress bar adapts: shows step numbers only on mobile (no labels to save space).

### Touch Targets
All interactive elements on mobile have a minimum touch target of 44x44px (per Apple HIG and WCAG 2.5.5). Icon buttons in tight layouts use negative margin with padding to expand the hit area without affecting visual layout.

### Typography Scale

| Element | Desktop | Mobile |
|---|---|---|
| H1 (page titles) | 28px / 500 weight | 22px / 500 |
| H2 (section heads) | 20px / 500 | 18px / 500 |
| Body | 15px / 400 | 15px / 400 |
| Small / Muted | 13px / 400 | 13px / 400 |
| FamilyFitScore (lg) | 56px / 600 | 48px / 600 |
| CategoryScore | 24px / 600 | 22px / 600 |

---

## 8. Data & Loading Strategy

### Optimistic UI
Save-to-shortlist actions are optimistic: the UI updates immediately and reverts only if the server returns an error.

### Streaming AI Responses
AI Advisor and the AI evaluation report narrative use streaming responses via the FastAPI backend. The frontend renders tokens as they arrive using `ReadableStream`. A blinking cursor is shown at the end of the streaming text until completion.

### Page Load Priority
On the Property Evaluation Report, sections load in this order:
1. Property snapshot (static data from DB) — appears immediately
2. Category scores (available once AI pipeline completes) — skeleton until ready
3. Family Fit Score — animates in when scores arrive
4. Per-person impact cards — load after main scores
5. Full AI narrative — streams in last

### Error Boundaries
Each major section on the Dashboard and Property Report is wrapped in an error boundary. If one section fails to load, it shows a muted card: "This section couldn't load. Refresh to try again." Other sections continue to display normally.

---

*End of GC Move OS UX Specification v1.0*
