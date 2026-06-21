# Gold Coast Move OS — AI Architecture
**Document 4 of 7 | Version 1.0 | June 2026**

---

## 1. AI System Overview

### 1.1 What AI Does in This Product

Gold Coast Move OS uses AI in seven distinct roles. These are not interchangeable — each role uses a different model, different temperature, different prompt structure, and has different failure modes and fallback strategies.

| Role | Description | Model | Primary Output |
|---|---|---|---|
| 1. Property Extraction | Extract structured data from listing HTML | GPT-4o-mini | JSON property record |
| 2. Property Scoring | Generate narrative and sub-score commentary | GPT-4o | Scoring commentary + reasoning |
| 3. Suburb Intelligence | Generate suburb community assessments | GPT-4o | Community narrative |
| 4. Recommendation Generation | Synthesise all scores into actionable recommendation | GPT-4o | Full evaluation output |
| 5. AI Advisor | Conversational relocation advisor | GPT-4o | Chat replies + preference signals |
| 6. Preference Learning | Extract preference signals from behaviour and conversation | GPT-4o-mini | Preference event records |
| 7. Five-Year Prediction | Reason about long-term life outcomes | GPT-4o | Structured outcome prediction |

### 1.2 Model Selection Rationale

**GPT-4o** is used wherever the output requires nuanced reasoning, family-specific context integration, or the output is directly shown to users as the product's core value. Accuracy and tone matter more than speed or cost.

**GPT-4o-mini** is used for high-volume, lower-stakes tasks: property data extraction from HTML (structured output, low ambiguity), preference signal detection from text, and initial data classification. The cost difference is approximately 15x, making this distinction important at scale.

**Decision rule:** If the user sees the output as part of their recommendation, use GPT-4o. If the output is a structured intermediate record feeding a downstream process, use GPT-4o-mini.

### 1.3 Cost Management Strategy

- AI scoring narratives are generated once per evaluation and stored. Re-evaluation rewrites them only if the family profile changes significantly.
- Suburb and school narratives are cached per suburb/school and reused across all families. These are expensive one-time costs.
- Advisor conversations are bounded: context window is managed via memory compression (summarise threads older than 20 messages rather than including raw history).
- Preference learning uses GPT-4o-mini, not GPT-4o, for every feedback event.
- OpenAI responses are stored in the database for auditability and to avoid re-calling the API for the same inputs.

---

## 2. Property Data Extraction (AI Role 1)

### 2.1 Overview

The user provides a URL. The system fetches the HTML, strips it with BeautifulSoup to extract the main content region (property title, description, details, and feature list), and sends the cleaned text to GPT-4o-mini for structured extraction. The goal is to produce a clean `ExtractedPropertyData` record.

### 2.2 HTML Pre-Processing

Before sending to OpenAI, the HTML is cleaned:
1. Parse with BeautifulSoup
2. Remove `<script>`, `<style>`, `<nav>`, `<footer>`, `<header>` tags
3. Extract the main content div (class patterns: `property-info`, `listing-details`, `property-details` — known for each domain)
4. Truncate to 8,000 characters (the meaningful data fits within this)
5. Strip HTML tags, preserve line breaks

This reduces token cost significantly and improves extraction accuracy by removing noise.

### 2.3 Extraction System Prompt

```
You are a property data extraction specialist. You will be given the text content of an Australian real estate listing page. Your task is to extract structured property data into the exact JSON format specified.

Rules:
- Extract only what is explicitly stated. Do not infer.
- If a field is not mentioned, set it to null.
- For price_guide: extract the listed price or range. If it says "contact agent" or "offers over", capture the number if present.
- For features: create one entry per distinct feature mentioned (pool, home office, air conditioning, etc.)
- For bedrooms/bathrooms/car_spaces: extract integers only.
- For land_size: extract number in square metres. If stated in acres, convert (1 acre = 4047 sqm).
- Set extraction_confidence for each field from 0.0 to 1.0 based on how clearly it was stated.

IMPORTANT: Return ONLY valid JSON. No explanation. No preamble. No code fences.
```

### 2.4 Extraction Output Schema

```typescript
interface ExtractedPropertyData {
  address: string | null
  suburb: string | null
  state: string | null
  postcode: string | null
  price_guide: number | null                 // Single number or midpoint of range
  price_guide_display: string | null         // Original string e.g. "$1.8m - $1.95m"
  bedrooms: number | null
  bathrooms: number | null
  car_spaces: number | null
  land_size: number | null                   // sqm
  property_type: string | null              // "house", "townhouse", etc.
  listing_description: string | null
  listing_agent: string | null
  listing_date: string | null
  features: ExtractedFeature[]
  field_confidence: Record<string, number>  // Per-field confidence 0.0-1.0
  overall_confidence: number                // Aggregate confidence
}

interface ExtractedFeature {
  name: string          // "pool", "home_office", "air_conditioning", etc.
  value: string | boolean | number | null
  confidence: number
}
```

### 2.5 Validation and Fallback

The OpenAI response is parsed and validated against the Pydantic `ExtractedPropertyData` schema. If parsing fails:

1. **Attempt 1:** Re-try with the same prompt (handles transient model errors)
2. **Attempt 2:** Use a stricter prompt with explicit output template
3. **Attempt 3 (final):** Mark the property as `extraction_failed`, store the raw text, notify the user that automatic extraction failed and ask them to confirm key details manually

Critical fields that fail validation (address, suburb) cause the extraction to fail. Non-critical fields (car_spaces, land_size) are allowed to be null and incur a confidence penalty only.

### 2.6 Confidence Penalty System

Extraction confidence feeds directly into the final Recommendation Confidence Score:

```python
def calculate_extraction_confidence(extracted: ExtractedPropertyData) -> float:
    penalties = {
        'address': 0.25 if extracted.address is None else 0,
        'price_guide': 0.15 if extracted.price_guide is None else 0,
        'bedrooms': 0.05 if extracted.bedrooms is None else 0,
        'bathrooms': 0.05 if extracted.bathrooms is None else 0,
        'land_size': 0.05 if extracted.land_size is None else 0,
        'listing_description': 0.10 if not extracted.listing_description else 0,
        'features': 0.10 if len(extracted.features) < 3 else 0,
    }
    return max(0.0, 1.0 - sum(penalties.values()))
```

---

## 3. Property Scoring AI (AI Role 2)

### 3.1 Architecture Decision

Scores are computed deterministically from structured data. AI generates the narrative commentary and provides nuanced justification — it does NOT own the numbers. This separation means scores are reproducible and auditable, while narratives are human-readable and family-specific.

The exception: where data is ambiguous (e.g. assessing "indoor-outdoor flow" from a listing description + images), AI contributes a soft score input that is bounded and validated before use.

### 3.2 Family Context Injection

Every scoring call receives a serialised family context block. This is the same block used across all AI roles and is defined in Section 10.

### 3.3 Property Scoring Prompt

```
You are a property assessment specialist for a family relocation platform.

You will be given:
1. A structured property data record
2. The family profile
3. The family's confirmed preferences and memories

Your task is to evaluate this property against this specific family's needs and generate:
1. A score (0-100) for each sub-dimension of Property Quality
2. A narrative commentary (2-3 sentences) for each dimension
3. A list of what this family will likely love about this property
4. A list of concerns or limitations for this family

Property Quality Dimensions:
- Modernity (0-100): Age of construction, interior quality signals, renovation status
- Design Quality (0-100): Architectural appeal, aesthetic coherence
- Indoor-Outdoor Flow (0-100): Connection between living areas and outdoor spaces
- Pool Quality (0-100): Presence, apparent size/quality, suitability for family use
- Home Office Suitability (0-100): Dedicated space, separation from living areas
- Entertaining Space (0-100): Kitchen quality, dining/outdoor entertaining capability
- Privacy (0-100): Street setback, fence height, overlooking neighbours
- Block Utility (0-100): Yard size, usable space, orientation

Scoring rules:
- If a feature is absent but required by the family (e.g. pool), score that dimension 0 and flag as critical
- Base your assessment on the listing description and features provided
- Do not inflate scores. Be direct. This family is making a major life decision.
- Reference specific family members when relevant (e.g. "Susie will likely appreciate...")

Output format: Return valid JSON only, matching the PropertyScoringOutput schema.
```

### 3.4 Function Calling Schema for Property Scoring

```python
property_scoring_function = {
    "name": "submit_property_score",
    "description": "Submit the scored property evaluation with narrative commentary",
    "parameters": {
        "type": "object",
        "properties": {
            "sub_scores": {
                "type": "object",
                "properties": {
                    "modernity": {"type": "number", "minimum": 0, "maximum": 100},
                    "design_quality": {"type": "number", "minimum": 0, "maximum": 100},
                    "indoor_outdoor_flow": {"type": "number", "minimum": 0, "maximum": 100},
                    "pool_quality": {"type": "number", "minimum": 0, "maximum": 100},
                    "home_office_suitability": {"type": "number", "minimum": 0, "maximum": 100},
                    "entertaining_space": {"type": "number", "minimum": 0, "maximum": 100},
                    "privacy": {"type": "number", "minimum": 0, "maximum": 100},
                    "block_utility": {"type": "number", "minimum": 0, "maximum": 100},
                },
                "required": ["modernity", "design_quality", "indoor_outdoor_flow", "pool_quality",
                             "home_office_suitability", "entertaining_space", "privacy", "block_utility"]
            },
            "narratives": {
                "type": "object",
                "properties": {
                    "modernity": {"type": "string"},
                    "indoor_outdoor_flow": {"type": "string"},
                    "pool": {"type": "string"},
                    "home_office": {"type": "string"},
                    "entertaining": {"type": "string"},
                    "overall": {"type": "string"},
                }
            },
            "family_positives": {
                "type": "array",
                "items": {"type": "string"},
                "description": "What this specific family will love about this property"
            },
            "family_concerns": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Concerns or limitations relevant to this specific family"
            },
            "critical_flags": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "attribute": {"type": "string"},
                        "description": {"type": "string"},
                        "is_deal_breaker": {"type": "boolean"}
                    }
                }
            }
        },
        "required": ["sub_scores", "narratives", "family_positives", "family_concerns", "critical_flags"]
    }
}
```

---

## 4. Community and Suburb Intelligence (AI Role 3)

### 4.1 Overview

Suburb narratives are generated once and cached. They are not family-specific (the family-specific interpretation happens in the Recommendation Generation step). Each suburb gets a community assessment that describes the suburb's character, demographic profile, lifestyle texture, and suitability for families.

### 4.2 Data Inputs to Suburb Narrative Prompt

```python
suburb_context = {
    "name": suburb.name,
    "postcode": suburb.postcode,
    "population": suburb.population,
    "owner_occupier_rate": suburb.owner_occupier_rate,
    "median_income": suburb.median_income,
    "crime_index": suburb.crime_index,
    "family_density": suburb.family_density,
    "educational_attainment": suburb.educational_attainment,
    "community_score": suburb.community_score,
    "lifestyle_score": suburb.lifestyle_score,
    "lifestyle_metrics": [
        {"name": m.name, "value": m.value} for m in suburb.metrics
    ],
    "schools": [
        {"name": s.name, "type": s.type, "school_score": s.school_score}
        for s in suburb.schools
    ],
    "distance_to_burleigh_km": suburb.distance_to_burleigh_km,
}
```

### 4.3 Suburb Intelligence Prompt

```
You are a Gold Coast community analyst specialising in helping families understand suburb character, not just suburb statistics.

You will be given demographic and lifestyle data for a Gold Coast suburb. Your task is to write three assessments:

1. COMMUNITY CHARACTER (150 words): Describe who lives here, what the community feels like, and what a new family would likely experience socially. Be specific about demographic composition, community cohesion signals, and lifestyle orientation. Avoid generic phrases.

2. LIFESTYLE TEXTURE (100 words): What is the day-to-day lifestyle experience in this suburb? What can you walk to? What is the rhythm of the area? What kind of family suits this suburb?

3. FAMILY FIT SUMMARY (75 words): In plain language, which type of family would thrive here, and why? Which type of family would struggle? Be direct.

Important: Write for a family that is seriously considering relocating. They need honest, specific information — not marketing copy. If the suburb has weaknesses relevant to families, state them plainly.
```

### 4.4 Family-Specific Suburb Interpretation

When a family evaluates a property in a suburb, the stored suburb narrative is combined with the family's specific context to generate the Community Score narrative for their evaluation. The Community Score itself is computed from the structured suburb metrics, not from AI.

---

## 5. Recommendation Generation (AI Role 4)

### 5.1 Architecture

The Recommendation Generation step is the most complex AI call in the system. It receives the outputs of all scoring services and synthesises them into the complete evaluation output the user sees: the executive summary, per-member impacts, trade-offs, verifications, and the final recommendation.

The family_fit_score and recommendation tier are already computed deterministically before this call. The AI's job is to generate the narrative layer that makes those numbers understandable and actionable.

### 5.2 Complete System Prompt

```
You are the Gold Coast Move OS family relocation advisor. You are direct, opinionated, and honest. You work for the family, not for any property or suburb.

Your core philosophy: the most important question is "Will this family likely have a better life here in five years?"

You have been given:
1. A full property record
2. The suburb data and community scores
3. The school ecosystem data
4. All category scores (community, lifestyle, school, property, financial)
5. Risk flags identified during evaluation
6. The family's complete profile including all members
7. The family's confirmed preferences and memories
8. A five-year outcome prediction
9. A recommendation tier already calculated (Ignore/Monitor/Inspect/Prioritise)

Your task is to generate the complete evaluation narrative. You must:

A. Write an EXECUTIVE SUMMARY (120 words max): The most important thing this family needs to know about this property. Start with the recommendation tier and why. Reference the family by name. Be specific, not generic.

B. Write a COMMUNITY NARRATIVE (80 words): How well does this suburb's community match what this family needs? Reference owner occupier rate, family density, and community character.

C. Write a LIFESTYLE NARRATIVE (80 words): How well does this suburb serve this family's daily lifestyle needs? Reference Burleigh access, beach access, wellness infrastructure, and the specific lifestyle priorities of family members.

D. Write a SCHOOL NARRATIVE (80 words): What is the school ecosystem like? How does it fit Austin's needs specifically? Reference commute and school community quality, not just academic ranking.

E. Write a PROPERTY NARRATIVE (80 words): What makes this property work or not work for this specific family? Reference Susie's aesthetic priorities, Ronnie's home office need, Austin's outdoor space, and Mabel's yard.

F. Write a FINANCIAL NARRATIVE (60 words): Is this property good value for this family? Are there financial risks?

G. Write MEMBER IMPACTS for each person:
   - Ronnie: What he'll love and what may concern him (50 words each)
   - Susie: What she'll love and what may concern her (50 words each)
   - Austin: Positives and concerns from a 7-year-old's perspective (40 words each)
   - Mabel: Yard, walkability, and safety assessment (30 words)

H. List 3-5 TRADE-OFFS: The honest tensions in this property. Format as short declarative sentences.

I. List 3-5 WHAT TO VERIFY: Specific things this family must check before proceeding. Be concrete — not "check the condition" but "verify the school catchment boundary as this property is near the edge" or "check for flood risk on the specific lot, not just the suburb average."

J. List 2-3 WHAT YOU MAY REGRET: Honest concerns about what could disappoint this family 1-2 years after moving in. These are the things they might not notice during an inspection but will feel over time.

K. Write a NEXT ACTION: One sentence. Specific. What should this family do next, and when?

Tone rules:
- Never use the phrase "great family home"
- Never say "you won't be disappointed"
- Never use "hidden gem"
- Be as specific as the data allows
- If data is missing, say so — don't invent
- Name the family members by name
- Reference confirmed family preferences when they are relevant
```

### 5.3 Recommendation Generation Function Schema

```python
recommendation_generation_function = {
    "name": "submit_recommendation",
    "description": "Submit the complete property recommendation and evaluation narrative",
    "parameters": {
        "type": "object",
        "properties": {
            "executive_summary": {"type": "string"},
            "community_narrative": {"type": "string"},
            "lifestyle_narrative": {"type": "string"},
            "school_narrative": {"type": "string"},
            "property_narrative": {"type": "string"},
            "financial_narrative": {"type": "string"},
            "member_impacts": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "member_name": {"type": "string"},
                        "role": {"type": "string"},
                        "positives": {"type": "array", "items": {"type": "string"}},
                        "concerns": {"type": "array", "items": {"type": "string"}},
                        "summary": {"type": "string"}
                    },
                    "required": ["member_name", "positives", "concerns", "summary"]
                }
            },
            "trade_offs": {"type": "array", "items": {"type": "string"}},
            "what_to_verify": {"type": "array", "items": {"type": "string"}},
            "what_you_may_regret": {"type": "array", "items": {"type": "string"}},
            "next_action": {"type": "string"}
        },
        "required": [
            "executive_summary", "community_narrative", "lifestyle_narrative",
            "school_narrative", "property_narrative", "financial_narrative",
            "member_impacts", "trade_offs", "what_to_verify",
            "what_you_may_regret", "next_action"
        ]
    }
}
```

---

## 6. AI Advisor / Conversational Interface (AI Role 5)

### 6.1 Architecture

The advisor is a persistent, stateful chat interface. It has access to the family's full context: all memories, the current shortlist, recent evaluations, and preferences. It can answer questions, help clarify trade-offs, and generate new evaluations on request. It also extracts preference signals from conversation and feeds them into the preference learning engine.

Thread management: Each conversation session is a thread. Threads older than 20 messages are compressed to a summary. The most recent 20 messages are always included in full. The system prompt + family context is injected on every call.

### 6.2 Base System Prompt (Full)

```
You are the Gold Coast Move OS advisor. You help families make better relocation decisions by giving honest, specific, evidence-based guidance.

You are not a search engine. You are not a real estate agent. You are a trusted advisor who has studied this family in detail and genuinely wants them to make the best decision for their life.

ABOUT THIS FAMILY:
{family_context_block}

YOUR ROLE:
- Answer questions about specific properties, suburbs, and schools using the data available
- Help the family understand trade-offs and tensions in their decision
- Notice when the family says something that reveals a preference — capture it
- Be honest when data is insufficient to answer a question
- Suggest next steps that are specific and actionable
- Remember what the family has said in previous conversations
- Challenge assumptions when the family appears to be making a decision based on incomplete information

COMMUNICATION STYLE:
- Direct and honest. Never vague.
- Warm but not sycophantic. Do not start every response with affirmation.
- Name family members by name when discussing their specific needs
- Prefer short paragraphs over long ones
- If you don't know something, say so. Never make up suburb statistics or school data.
- When the family expresses doubt or confusion, explore it — don't dismiss it
- When asked for a recommendation, give one. Don't hedge endlessly.

CURRENT CONTEXT:
- Active shortlist: {shortlist_summary}
- Properties currently under evaluation: {pending_evaluations}
- Most recent evaluation: {most_recent_evaluation_summary}
- Family's current top concerns: {top_concerns_from_memory}

AVAILABLE TOOLS:
You have access to functions that allow you to:
- Look up property details by ID
- Look up suburb data
- Look up school data
- Trigger a new property evaluation
- Add a memory to the family's memory store
- Create a decision journal entry
- Log a preference signal

Use these tools when the user asks about specific data or when you detect a preference signal worth capturing.

PREFERENCE SIGNAL DETECTION:
Whenever the user says something that reveals a preference, concern, or priority — capture it using the log_preference_signal function. Do not tell the user you are doing this. Examples:
- "That feels too far from the beach" → BurleighAccess / Negative / Strength 4
- "I love that kitchen" → KitchenQuality / Positive / Strength 3
- "Austin would hate not having kids on the street" → ChildFriendlyStreet / Positive / Strength 5

IMPORTANT LIMITS:
- You cannot access the internet. Do not make claims about current property prices or listings you have not been given data about.
- Do not recommend specific properties to make an offer on — that is the family's decision.
- Always include appropriate uncertainty when predicting future outcomes.
```

### 6.3 Advisor Function Calling Tools

```python
advisor_tools = [
    {
        "name": "get_property_details",
        "description": "Retrieve full details and evaluation for a specific property",
        "parameters": {
            "type": "object",
            "properties": {
                "property_id": {"type": "string", "description": "The property ID"}
            },
            "required": ["property_id"]
        }
    },
    {
        "name": "get_suburb_details",
        "description": "Retrieve suburb data and community assessment",
        "parameters": {
            "type": "object",
            "properties": {
                "suburb_name": {"type": "string", "description": "Name of the suburb"}
            },
            "required": ["suburb_name"]
        }
    },
    {
        "name": "get_school_details",
        "description": "Retrieve school profile and scores",
        "parameters": {
            "type": "object",
            "properties": {
                "school_name": {"type": "string", "description": "Name of the school"}
            },
            "required": ["school_name"]
        }
    },
    {
        "name": "log_preference_signal",
        "description": "Capture a family preference signal detected from the conversation",
        "parameters": {
            "type": "object",
            "properties": {
                "attribute": {"type": "string", "description": "The preference attribute (e.g. BurleighAccess, PoolQuality)"},
                "sentiment": {"type": "string", "enum": ["Positive", "Negative", "Neutral", "Concern", "DealBreaker"]},
                "strength": {"type": "integer", "minimum": 1, "maximum": 5},
                "member_name": {"type": "string", "description": "Which family member expressed this (if known)"},
                "evidence_text": {"type": "string", "description": "The exact text that revealed this preference"}
            },
            "required": ["attribute", "sentiment", "strength", "evidence_text"]
        }
    },
    {
        "name": "create_journal_entry",
        "description": "Create a decision journal entry based on the conversation",
        "parameters": {
            "type": "object",
            "properties": {
                "entry_type": {"type": "string", "enum": ["FamilyDiscussion", "Concern", "DecisionChange"]},
                "title": {"type": "string"},
                "summary": {"type": "string"},
                "decision": {"type": "string"},
                "related_property_id": {"type": "string"}
            },
            "required": ["entry_type", "title", "summary"]
        }
    },
    {
        "name": "add_family_memory",
        "description": "Add or update a family memory based on something important said in conversation",
        "parameters": {
            "type": "object",
            "properties": {
                "memory_type": {"type": "string", "enum": ["Preference", "Learned", "Decision"]},
                "subject": {"type": "string"},
                "value": {"type": "string", "description": "The memory content"},
                "confidence": {"type": "number", "minimum": 0.0, "maximum": 1.0},
                "source": {"type": "string", "enum": ["UserStated", "AIInferred"]}
            },
            "required": ["memory_type", "subject", "value", "confidence", "source"]
        }
    }
]
```

### 6.4 Thread Management Strategy

```python
# services/advisor.py
MAX_MESSAGES_IN_CONTEXT = 20
SUMMARY_TRIGGER = 30  # Summarise when thread exceeds 30 messages

async def build_conversation_context(thread_id: str, family_id: str) -> list[dict]:
    messages = await get_thread_messages(thread_id)

    if len(messages) <= MAX_MESSAGES_IN_CONTEXT:
        return messages

    # Older messages: include compressed summary only
    old_messages = messages[:-MAX_MESSAGES_IN_CONTEXT]
    recent_messages = messages[-MAX_MESSAGES_IN_CONTEXT:]

    summary = await compress_thread_history(old_messages)
    summary_message = {
        "role": "system",
        "content": f"[Previous conversation summary]: {summary}"
    }

    return [summary_message] + recent_messages
```

---

## 7. Preference Learning AI (AI Role 6)

### 7.1 Overview

Preference learning runs after every meaningful user interaction: property save, property reject, feedback submission, and advisor conversation. It uses GPT-4o-mini (not GPT-4o) because the task is well-defined signal extraction from text, not nuanced reasoning.

### 7.2 Preference Signal Extraction Prompt

```
You are a preference signal extractor for a family relocation platform.

You will be given text from one of these sources:
- A user comment on a property
- A property rating with notes
- An inspection feedback note
- A snippet from an advisor conversation
- A property save or reject action with optional reason

Your task is to identify all preference signals embedded in this text.

A preference signal is a statement that reveals something the family values, dislikes, or feels uncertain about in the context of choosing a home or suburb.

For each signal, output:
- attribute: what the signal is about (standardised term from the attribute list)
- sentiment: Positive / Negative / Neutral / Concern / DealBreaker
- strength: 1-5 (1 = weak, 5 = critical/deal-breaker)
- member_id: which family member, if identifiable from context
- evidence_text: the exact phrase that revealed the signal
- confidence: 0.0-1.0 how confident you are this is a genuine signal

Attribute list:
BurleighAccess, BeachAccess, PoolQuality, HomeOffice, ModernInterior, CoastalAesthetic,
LargeKitchen, IndoorOutdoorFlow, EntertainingSpace, Yard, StreetSafety, FloodRisk,
SchoolCommunity, SchoolCommute, ChildFriendlyStreet, WellnessInfrastructure,
PeerGroup, CommunityQuality, LandSize, Privacy, Modernity, AcademicOutcomes,
WalkabilityForDog, Cafes, RoadNoise, PriceValue, SuburbPrestige

If no preference signals are present, return an empty array.

Output: valid JSON array only. No explanation.
```

### 7.3 Preference Weight Update Logic

```python
# services/preference_learning.py
async def update_preferences_from_signals(family_id: str, signals: list[PreferenceSignal]):
    for signal in signals:
        pref = await get_or_create_preference(family_id, signal.attribute, signal.member_id)

        if signal.sentiment in ['Positive']:
            pref.positive_signals += 1
            pref.current_weight = min(5, pref.current_weight + (signal.strength * 0.1))
        elif signal.sentiment in ['Negative', 'Concern']:
            pref.negative_signals += 1
            pref.current_weight = max(0, pref.current_weight - (signal.strength * 0.05))
        elif signal.sentiment == 'DealBreaker':
            pref.current_weight = 5
            pref.status = 'Manual'

        # Update confidence based on signal count
        total_signals = pref.positive_signals + pref.negative_signals
        agreement_ratio = pref.positive_signals / max(1, total_signals)

        if total_signals >= 3 and agreement_ratio >= 0.75:
            pref.status = 'Confirmed'
            pref.confidence = min(0.95, 0.5 + (total_signals * 0.05))
        elif pref.positive_signals > 0 and pref.negative_signals > 0:
            pref.status = 'Contradicted'
            pref.confidence *= 0.7  # Reduce confidence on contradiction

        await save_preference(pref)
```

### 7.4 Contradiction Detection

When a preference moves to `Contradicted` status, the system generates a user-facing prompt via the advisor:

```
"Based on your recent activity, you appear to be warming to {suburb} despite previously expressing concerns about {attribute}. Should we revisit your preference for this area? Your evaluation scores will be updated if you confirm."
```

---

## 8. Five-Year Outcome Prediction (AI Role 7)

### 8.1 Overview

The Five-Year Fit Score is the product's most distinctive output. It answers: "Will this family likely have a better life here in five years?" It is computed as a weighted score (see formula below) but the narrative reasoning is AI-generated and family-specific.

### 8.2 Score Components and Weighting

```python
five_year_weights = {
    "community_belonging": 0.20,
    "child_friendships": 0.15,
    "parent_friendships": 0.15,
    "lifestyle_improvement": 0.15,
    "school_fit": 0.15,
    "home_satisfaction": 0.10,
    "financial_comfort": 0.05,
    "regret_risk": 0.05,   # Inverted: high regret risk = lower score
}
```

Each component is scored 0-100 by the AI using structured function calling (not free text). The weighted sum produces the Five-Year Fit Score. The AI then generates a narrative explaining the reasoning.

### 8.3 Five-Year Prediction System Prompt

```
You are a long-term life outcome assessor for a family relocation platform.

Your task is to estimate, with structured reasoning, how likely it is that this family will look back in five years and feel their move to the Gold Coast was the right decision — specifically to this property and suburb.

This is NOT a property valuation exercise. You are assessing quality of life outcomes.

You have been given:
- The complete property and suburb evaluation
- The family profile and individual member needs
- The family's confirmed preferences and memories
- All scoring results from the evaluation

You must score each dimension from 0 to 100:

COMMUNITY BELONGING (0-100)
How likely is this family to form genuine friendships and feel part of the community in this suburb within 2 years? Consider: family density, owner-occupier rate, demographic alignment, community infrastructure.

CHILD FRIENDSHIPS (0-100)
How likely is Austin (age 7) to make strong, lasting friendships here? Consider: number of families with similar-aged children, school community quality, street type, parks and outdoor spaces.

PARENT FRIENDSHIPS (0-100)
How likely are Ronnie and Susie to find their peer group here? Consider: educational attainment, income levels, lifestyle orientation of the suburb demographic, school parent community.

LIFESTYLE IMPROVEMENT (0-100)
How significantly is this move likely to improve the family's daily lifestyle quality? Consider: Burleigh access, beach access, wellness infrastructure, cafe culture, Susie's lifestyle priorities, Ronnie's wellness focus.

SCHOOL FIT (0-100)
How well will this property's school options serve Austin's development needs? Consider: wellbeing score, parent community, commute, confidence-building culture.

HOME SATISFACTION (0-100)
How satisfied will the family be with this specific property after 2 years of living in it? Consider: Susie's aesthetic priorities, functional fit, pool quality, home office, entertaining capacity.

FINANCIAL COMFORT (0-100)
How financially secure is this decision likely to feel in 5 years? Consider: price relative to budget, suburb growth trajectory, mortgage stress risk.

REGRET RISK (0-100)
How HIGH is the risk that the family will regret this specific choice? Score 100 if regret is very likely. This score is INVERTED in the final calculation.

After scoring, write a FIVE-YEAR NARRATIVE (150 words): Paint a specific, honest picture of what this family's life might look like five years after moving here. Use names. Be specific about what has worked and what has been harder than expected. Do not make it uniformly positive.

Then write the UNCERTAINTY STATEMENT: Two sentences acknowledging what the model cannot know and what the family must discover themselves.

Output: valid JSON using the five_year_prediction function schema.
```

### 8.4 Required Uncertainty Disclosure

Every five-year prediction output must include a standardised uncertainty disclosure. This is not optional. It is appended to every five-year narrative shown to users:

```
This is a structured prediction based on available data, not a guarantee. The biggest unknowns — actual street feel, the specific parent community at {school_name}, and whether the day-to-day lifestyle rhythm feels natural to your family — can only be discovered by visiting in person.
```

### 8.5 Five-Year Prediction Function Schema

```python
five_year_prediction_function = {
    "name": "submit_five_year_prediction",
    "description": "Submit the five-year life outcome prediction for this property and family",
    "parameters": {
        "type": "object",
        "properties": {
            "scores": {
                "type": "object",
                "properties": {
                    "community_belonging": {"type": "number", "minimum": 0, "maximum": 100},
                    "child_friendships": {"type": "number", "minimum": 0, "maximum": 100},
                    "parent_friendships": {"type": "number", "minimum": 0, "maximum": 100},
                    "lifestyle_improvement": {"type": "number", "minimum": 0, "maximum": 100},
                    "school_fit": {"type": "number", "minimum": 0, "maximum": 100},
                    "home_satisfaction": {"type": "number", "minimum": 0, "maximum": 100},
                    "financial_comfort": {"type": "number", "minimum": 0, "maximum": 100},
                    "regret_risk": {"type": "number", "minimum": 0, "maximum": 100},
                },
                "required": ["community_belonging", "child_friendships", "parent_friendships",
                             "lifestyle_improvement", "school_fit", "home_satisfaction",
                             "financial_comfort", "regret_risk"]
            },
            "score_reasoning": {
                "type": "object",
                "description": "One sentence justification for each score",
                "additionalProperties": {"type": "string"}
            },
            "five_year_narrative": {"type": "string"},
            "key_success_factors": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Top 3 reasons this is likely to succeed"
            },
            "key_risk_factors": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Top 2-3 things that could make this fall short of expectations"
            },
            "uncertainty_statement": {"type": "string"}
        },
        "required": ["scores", "score_reasoning", "five_year_narrative",
                     "key_success_factors", "key_risk_factors", "uncertainty_statement"]
    }
}
```

---

## 9. Prompt Engineering Standards

### 9.1 System Prompt Template Structure

Every prompt in the system follows this order:

```
1. ROLE DEFINITION (1-2 sentences): What this AI instance is and who it serves
2. PHILOSOPHY (1-2 sentences): The core evaluative principle (life outcomes > property features)
3. INPUTS (explicit list of what the model has received)
4. TASK (numbered list of exactly what to do)
5. TONE RULES (what to avoid, what to prefer)
6. OUTPUT FORMAT (JSON schema or explicit structure)
7. CRITICAL RULES (overrides, fallbacks, hard constraints)
```

### 9.2 Family Context Block (Always Injected)

The family context block is serialised as a structured JSON string and injected into every system prompt that requires family-specific reasoning. This is assembled server-side before every AI call.

```python
def build_family_context_block(family: Family, members: list[FamilyMember],
                                 memories: list[FamilyMemory],
                                 preferences: list[FamilyPreference]) -> str:
    confirmed_preferences = [p for p in preferences if p.status == 'Confirmed']
    high_confidence_memories = [m for m in memories if m.confidence >= 0.65]

    return json.dumps({
        "family_name": family.family_name,
        "budget_range": f"${family.budget_min:,} - ${family.budget_max:,}",
        "move_timeframe": family.move_timeframe,
        "current_location": family.current_location,
        "members": [
            {
                "name": m.name,
                "role": m.role,
                "age": m.age,
                "primary_priorities": m.primary_priorities,
                "non_negotiables": m.non_negotiables,
            }
            for m in members
        ],
        "confirmed_preferences": [
            {
                "attribute": p.attribute,
                "weight": p.current_weight,
                "confidence": p.confidence,
                "member": p.member_name,
            }
            for p in confirmed_preferences
        ],
        "key_memories": [
            {
                "subject": m.subject,
                "value": m.value,
                "confidence": m.confidence,
                "type": m.memory_type,
            }
            for m in high_confidence_memories[:15]  # Cap at 15 to manage token budget
        ],
        "non_negotiables": [
            "Detached house", "Pool", "Home office", "Air conditioning",
            "Within 20 minutes of Burleigh", "Within 20 minutes of beach access",
            "Low flood risk", "Safe street", "Within budget",
        ],
    }, indent=2)
```

### 9.3 Temperature Settings

| Use Case | Temperature | Rationale |
|---|---|---|
| Property data extraction | 0.0 | Deterministic: extract facts, no creativity |
| Property scoring | 0.3 | Mostly structured, allow some variation in phrasing |
| Suburb narrative | 0.5 | Descriptive writing, some stylistic variation acceptable |
| Recommendation generation | 0.4 | Mostly consistent, narrative can vary |
| AI Advisor chat | 0.7 | Conversational, should feel natural and varied |
| Preference signal extraction | 0.0 | Deterministic classification task |
| Five-year prediction | 0.4 | Structured scoring + narrative |

### 9.4 Retry Logic and Fallback

```python
# utils/openai_client.py
async def call_with_retry(
    messages: list[dict],
    function: dict | None = None,
    model: str = "gpt-4o",
    temperature: float = 0.4,
    max_retries: int = 3,
) -> dict:
    last_error = None
    for attempt in range(max_retries):
        try:
            kwargs = {
                "model": model,
                "messages": messages,
                "temperature": temperature,
                "max_tokens": 4000,
            }
            if function:
                kwargs["tools"] = [{"type": "function", "function": function}]
                kwargs["tool_choice"] = {"type": "function", "function": {"name": function["name"]}}

            response = await openai.chat.completions.create(**kwargs)

            if function:
                tool_call = response.choices[0].message.tool_calls[0]
                return json.loads(tool_call.function.arguments)
            else:
                return {"content": response.choices[0].message.content}

        except openai.RateLimitError:
            await asyncio.sleep(2 ** attempt)  # Exponential backoff
            last_error = "rate_limit"
        except openai.APIError as e:
            if attempt < max_retries - 1:
                await asyncio.sleep(1)
            last_error = str(e)
        except json.JSONDecodeError:
            # Function calling returned invalid JSON — retry with lower temperature
            temperature = max(0.0, temperature - 0.1)
            last_error = "json_parse_error"

    raise AIServiceError(f"OpenAI call failed after {max_retries} attempts: {last_error}")
```

---

## 10. Context Window Management

### 10.1 Token Budget Allocation (Per Evaluation Call)

```
Total budget (GPT-4o): ~128k tokens
Practical limit per call: 12,000 tokens (cost-managed)

Allocation:
  System prompt (base):          ~800 tokens
  Family context block:          ~600 tokens
  Property data:                 ~400 tokens
  Suburb data:                   ~300 tokens
  School data:                   ~300 tokens
  Score results:                 ~200 tokens
  Memory block (capped at 15):   ~500 tokens
  Conversation history (advisor):~2,000 tokens
  Output budget:                 ~4,000 tokens
  Buffer:                        ~2,900 tokens
```

### 10.2 Memory Compression

When the family's memory store exceeds 15 high-confidence entries, older entries are compressed:

```python
# services/memory.py
async def get_prompt_ready_memories(family_id: str, max_memories: int = 15) -> list[FamilyMemory]:
    all_memories = await get_active_memories(family_id)

    # Always include permanent memories (non-negotiables, family profile facts)
    permanent = [m for m in all_memories if m.memory_type == 'Permanent']

    # Sort remaining by confidence descending, include top N
    learned_and_preference = [m for m in all_memories if m.memory_type != 'Permanent']
    learned_and_preference.sort(key=lambda m: m.confidence, reverse=True)

    combined = permanent + learned_and_preference
    return combined[:max_memories]
```

When advisor conversation threads grow beyond 30 messages, a compression call summarises the older portion:

```python
async def compress_thread_history(old_messages: list[dict]) -> str:
    compression_prompt = [
        {"role": "system", "content": "Summarise the following conversation between a family and their relocation advisor. Preserve all specific preferences expressed, properties discussed, and decisions made. Output in 200 words or fewer."},
        {"role": "user", "content": "\n".join([f"{m['role']}: {m['content']}" for m in old_messages])}
    ]
    result = await openai.chat.completions.create(
        model="gpt-4o-mini",
        messages=compression_prompt,
        temperature=0.0,
        max_tokens=400,
    )
    return result.choices[0].message.content
```

### 10.3 Truncation Rules

If a property listing description exceeds 3,000 characters, it is truncated to 3,000. If suburb data exceeds 2,000 characters, it is truncated. The truncation is logged so confidence penalties can be applied.

---

## 11. AI Cost Estimation

### 11.1 Token Usage Per Full Property Evaluation

| Step | Model | Input Tokens | Output Tokens | Cost (GPT-4o $2.50/1M in, $10/1M out) |
|---|---|---|---|---|
| Property extraction | GPT-4o-mini | 2,000 | 500 | $0.0003 |
| Property scoring | GPT-4o | 3,000 | 1,000 | $0.0175 |
| Community narrative* | GPT-4o | 1,500 | 600 | $0.0098 |
| Recommendation generation | GPT-4o | 5,000 | 2,500 | $0.0375 |
| Five-year prediction | GPT-4o | 4,000 | 1,500 | $0.0250 |
| Preference signal extraction | GPT-4o-mini | 800 | 300 | $0.00012 |
| **Total per evaluation** | | **~16,300** | **~6,400** | **~$0.090** |

*Community narrative cached per suburb. Amortised cost per evaluation = $0.002 after first 5 evaluations of that suburb.

### 11.2 Advisor Chat Cost

| Scenario | Input | Output | Cost |
|---|---|---|---|
| Short reply | 2,500 | 400 | $0.0103 |
| Long analysis | 4,000 | 1,200 | $0.0220 |
| Average per message | 3,000 | 700 | $0.0145 |

### 11.3 Monthly Cost Projection

| Scenario | Evaluations/month | Advisor Messages/month | Monthly AI Cost |
|---|---|---|---|
| MVP (5 families) | 100 | 200 | ~$12 |
| Early (50 families) | 500 | 800 | ~$57 |
| Growth (500 families) | 3,000 | 5,000 | ~$342 |
| Scale (2,000 families) | 10,000 | 15,000 | ~$1,118 |

AI costs are not a constraint until significant scale. Optimisation strategies are documented below.

### 11.4 Optimisation Strategies

1. **Suburb narrative caching**: Generate once per suburb, reuse for all families. Saves ~$0.01 per evaluation after the first.
2. **School narrative caching**: Same pattern as suburb.
3. **Extraction model downgrade**: GPT-4o-mini for extraction is already implemented. Saves ~$0.017 per evaluation vs using GPT-4o.
4. **Evaluation result caching**: If the same property is evaluated by multiple families (unlikely in MVP), cache the non-family-specific scoring components.
5. **Preference signal batching**: Batch multiple feedback events into a single signal extraction call instead of one call per event.
6. **Context compression**: Memory compression (Section 10.2) prevents context window bloat in long advisor sessions.

---

## 12. Complete OpenAI Function Calling Definitions

### 12.1 submit_property_score (Role 2)

Defined in Section 3.4 above.

### 12.2 submit_suburb_assessment

```python
suburb_assessment_function = {
    "name": "submit_suburb_assessment",
    "description": "Submit the community and lifestyle assessment for a suburb",
    "parameters": {
        "type": "object",
        "properties": {
            "community_character": {"type": "string", "description": "150-word community character description"},
            "lifestyle_texture": {"type": "string", "description": "100-word lifestyle description"},
            "family_fit_summary": {"type": "string", "description": "75-word family fit assessment"},
            "community_score_justification": {"type": "string"},
            "lifestyle_score_justification": {"type": "string"},
            "best_suited_family_type": {"type": "string"},
            "least_suited_family_type": {"type": "string"},
        },
        "required": ["community_character", "lifestyle_texture", "family_fit_summary",
                     "community_score_justification", "lifestyle_score_justification",
                     "best_suited_family_type", "least_suited_family_type"]
    }
}
```

### 12.3 submit_recommendation (Role 4)

Defined in Section 5.3 above.

### 12.4 submit_five_year_prediction (Role 7)

Defined in Section 8.5 above.

### 12.5 extract_property_data (Role 1)

```python
property_extraction_function = {
    "name": "extract_property_data",
    "description": "Extract structured property data from listing page content",
    "parameters": {
        "type": "object",
        "properties": {
            "address": {"type": ["string", "null"]},
            "suburb": {"type": ["string", "null"]},
            "state": {"type": ["string", "null"]},
            "postcode": {"type": ["string", "null"]},
            "price_guide": {"type": ["number", "null"], "description": "Numeric price in AUD"},
            "price_guide_display": {"type": ["string", "null"], "description": "Original price text"},
            "bedrooms": {"type": ["integer", "null"]},
            "bathrooms": {"type": ["integer", "null"]},
            "car_spaces": {"type": ["integer", "null"]},
            "land_size": {"type": ["number", "null"], "description": "Land size in square metres"},
            "property_type": {"type": ["string", "null"]},
            "listing_description": {"type": ["string", "null"]},
            "listing_agent": {"type": ["string", "null"]},
            "features": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string"},
                        "value": {},
                        "confidence": {"type": "number", "minimum": 0.0, "maximum": 1.0}
                    },
                    "required": ["name", "value", "confidence"]
                }
            },
            "field_confidence": {
                "type": "object",
                "description": "Per-field extraction confidence 0.0-1.0",
                "additionalProperties": {"type": "number"}
            },
            "overall_confidence": {"type": "number", "minimum": 0.0, "maximum": 1.0}
        },
        "required": ["address", "suburb", "price_guide", "bedrooms", "bathrooms",
                     "property_type", "features", "field_confidence", "overall_confidence"]
    }
}
```

### 12.6 extract_preference_signals (Role 6)

```python
preference_signal_extraction_function = {
    "name": "extract_preference_signals",
    "description": "Extract all preference signals from the provided text",
    "parameters": {
        "type": "object",
        "properties": {
            "signals": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "attribute": {"type": "string"},
                        "sentiment": {
                            "type": "string",
                            "enum": ["Positive", "Negative", "Neutral", "Concern", "DealBreaker"]
                        },
                        "strength": {"type": "integer", "minimum": 1, "maximum": 5},
                        "member_id": {"type": ["string", "null"]},
                        "evidence_text": {"type": "string"},
                        "confidence": {"type": "number", "minimum": 0.0, "maximum": 1.0}
                    },
                    "required": ["attribute", "sentiment", "strength", "evidence_text", "confidence"]
                }
            }
        },
        "required": ["signals"]
    }
}
```

---

*Document complete. These two documents (Technical Architecture and AI Architecture) together with the Project Bible form the complete implementation specification for the Gold Coast Move OS intelligence platform.*
