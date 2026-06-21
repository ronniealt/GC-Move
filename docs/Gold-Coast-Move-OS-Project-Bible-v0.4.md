# Gold Coast Move OS Project Bible v0.4

## Volume 4 – Family Decision Intelligence Engine

## Purpose of This Volume

This volume defines the core intelligence layer of the product.

The product is not merely a property search tool. It is a Family Decision Intelligence platform that helps a family make a major life decision with greater confidence.

The system must understand:

• Who the family is  
• What they value  
• What trade-offs they are willing to make  
• What they consistently like and reject  
• What outcomes they are trying to create  
• Which properties, suburbs and schools increase or reduce the probability of those outcomes

The Family Decision Intelligence Engine is the moat of the product.

---

# Chapter 31 – Family Profile Architecture

## Objective

Create a structured profile that represents the family as a decision-making unit while still preserving the individual needs of each family member.

## Core Entities

### Family

The Family entity represents the household making the relocation decision.

Recommended fields:

```text
FamilyID
FamilyName
CurrentLocation
TargetRegion
BudgetMin
BudgetMax
MoveTimeframe
PrimarySuccessMetric
CreatedAt
UpdatedAt
```

### Family Member

Each member of the family has their own needs, preferences and decision impact.

Recommended fields:

```text
FamilyMemberID
FamilyID
Name
Role
Age
LifeStage
PrimaryPriorities
SecondaryPriorities
NonNegotiables
CreatedAt
UpdatedAt
```

Example roles:

```text
Parent
Child
Pet
OtherDependent
```

## Current Family Profile Example

### Ronnie

Priorities:

• Better lifestyle  
• Less pressure  
• Strong community  
• Great family life  
• Strong school ecosystem  
• Quality home  
• Wellness-oriented lifestyle  
• Entrepreneurial and successful peer group

### Susie

Priorities:

• Beautiful modern home  
• Daily beach access  
• Wellness-focused environment  
• Cafes, restaurants, gyms and Pilates  
• Aesthetic appeal  
• Pride of ownership

### Austin

Priorities:

• Confidence  
• Resilience  
• Independence  
• Strong friendships  
• Positive school experience  
• Active outdoor lifestyle

### Mabel

Priorities:

• Suitable yard  
• Walkability  
• Parks  
• Safe environment

## Profile Design Principle

The system must not flatten the family into one generic user.

A property may be excellent for Ronnie but weak for Susie.

A suburb may be convenient for parents but poor for Austin’s friendships.

The system must make these tensions visible.

## Family-Level Success Metric

The master success metric remains:

```text
Five years after moving, the family can say:
"We improved our lifestyle, bought a beautiful home and built meaningful friendships within a strong community."
```

## Implementation Requirement

Every property evaluation must reference:

```text
FamilyID
FamilyMember impacts
Household-level fit
Individual-level fit
Trade-offs
Recommendation confidence
```

---

# Chapter 32 – Preference Capture Framework

## Objective

Capture explicit and implicit family preferences so the recommendation engine improves over time.

## Preference Types

### Explicit Preferences

Preferences directly stated by the family.

Examples:

```text
Must have pool
Must be detached house
Needs home office
Must be within budget
Must be within 20 minutes of beach access
Must be within 20 minutes of Burleigh lifestyle precinct
Prefer 5 bedrooms
Prefer modern coastal architecture
Prefer strong family community
Avoid high flood risk
Avoid unsafe streets
```

### Implicit Preferences

Preferences inferred from behaviour.

Examples:

```text
User repeatedly saves modern coastal homes
User rejects older brick homes
User spends more time reviewing properties in Robina
User consistently scores large entertaining areas highly
User shows concern about busy roads
User prefers homes with strong indoor-outdoor flow
```

### Learned Preferences

Preferences confirmed over multiple interactions.

Examples:

```text
Family consistently values community above prestige
Susie consistently prioritises aesthetic quality
Ronnie consistently prioritises peer group and school ecosystem
Austin’s needs increase the value of walkable family streets
Properties without strong outdoor space underperform
```

## Preference Event Model

Every meaningful user interaction should be captured as a PreferenceEvent.

Recommended fields:

```text
PreferenceEventID
FamilyID
FamilyMemberID optional
PropertyID optional
SuburbID optional
SchoolID optional
Attribute
Sentiment
Strength
Source
EvidenceText
CreatedAt
```

## Sentiment Values

```text
Positive
Negative
Neutral
Concern
DealBreaker
```

## Strength Scale

```text
1 = Weak signal
2 = Mild signal
3 = Moderate signal
4 = Strong signal
5 = Critical signal
```

## Source Values

```text
UserStated
UserRating
SavedProperty
RejectedProperty
Comment
InspectionNote
AIInferred
ManualOverride
```

## Capture Examples

### Example 1

Ronnie says:

```text
"This one feels too far from Burleigh."
```

Captured as:

```text
Attribute: BurleighAccess
Sentiment: Negative
Strength: 4
Source: UserStated
EvidenceText: This one feels too far from Burleigh.
```

### Example 2

Susie saves three homes with white interiors, coastal styling and large kitchens.

Captured as:

```text
Attribute: ModernCoastalAesthetic
Sentiment: Positive
Strength: 3
Source: AIInferred
EvidenceText: Repeated saves of modern coastal homes with light interiors.
```

## Implementation Requirement

The system must separate:

```text
What the family said
What the family did
What the system inferred
What has been confirmed over time
```

This prevents the recommendation engine from overreacting to one-off comments.

---

# Chapter 33 – Preference Learning Engine

## Objective

Turn repeated family interactions into a continuously improving decision model.

## Learning Principle

One interaction is a signal.

Repeated interaction is a preference.

Repeated preference across contexts becomes a decision rule.

## Preference Weighting

Each preference should maintain a dynamic weight.

Recommended fields:

```text
PreferenceID
FamilyID
FamilyMemberID optional
Attribute
CurrentWeight
Confidence
PositiveSignals
NegativeSignals
LastUpdated
Status
```

## Weight Scale

```text
0 = Ignore
1 = Minor preference
2 = Moderate preference
3 = Strong preference
4 = Major preference
5 = Non-negotiable
```

## Confidence Scale

```text
0.0 to 1.0
```

## Preference Status

```text
Emerging
Confirmed
Contradicted
Retired
Manual
```

## Learning Rules

### Rule 1 – Repetition Increases Confidence

If the same attribute receives three or more consistent positive signals, increase confidence.

Example:

```text
ModernCoastalDesign receives 3 positive signals
Confidence increases from 0.45 to 0.70
```

### Rule 2 – Contradiction Reduces Confidence

If the family previously rejected a feature but later saves multiple properties with that feature, reduce confidence and flag contradiction.

Example:

```text
Previously rejected: Varsity Lakes
Later saved: 4 Varsity Lakes homes
Action: mark SuburbPreference as Contradicted
```

### Rule 3 – Deal Breakers Override Scores

If an attribute is marked DealBreaker, it must override the weighted score.

Examples:

```text
High flood risk
Unsafe street
Outside budget
No pool
Attached dwelling
Poor school access
```

### Rule 4 – Person-Specific Preferences Matter

Susie’s aesthetic preferences should not be blended into Ronnie’s school/community preferences.

The system must store whose preference is being represented.

### Rule 5 – Family-Level Preferences Require Agreement

A preference becomes family-level only when it is:

```text
Stated by both parents
Repeatedly reflected in behaviour
Or manually confirmed
```

## Preference Learning Output

For each family, the system should generate:

```text
Things Ronnie Loves
Things Susie Loves
Things Austin Needs
Things Mabel Needs
Things Both Parents Love
Things The Family Rejects
Unresolved Trade-Offs
Emerging Preferences
```

## Implementation Requirement

After every property review, the system must update the preference model.

The update should include:

```text
New positive signals
New negative signals
Changed weights
Changed confidence
Contradictions
New decision rules
```

---

# Chapter 34 – Family Memory System

## Objective

Maintain continuity across sessions so the product behaves like an advisor that remembers the family.

## Memory Types

### Permanent Memory

Stable facts unlikely to change often.

Examples:

```text
Family members
Ages
Current location
Target region
Budget range
School preferences
Pet requirements
Non-negotiables
```

### Preference Memory

Known preferences that influence scoring.

Examples:

```text
Modern coastal homes
Pool
Home office
Strong family suburb
Daily beach access
Wellness culture
Low flood risk
Low crime
```

### Learned Memory

Patterns derived from repeated behaviour.

Examples:

```text
Family prefers community over prestige
Susie strongly values visual appeal
Ronnie cares about entrepreneurial peer group
Austin’s friendship opportunities are critical
Homes on busy roads are usually rejected
```

### Session Memory

Temporary active context.

Examples:

```text
Current shortlist
Recent properties reviewed
Current suburbs under consideration
Current doubts
Inspection notes
```

### Decision Memory

History of decisions and why they were made.

Examples:

```text
Property rejected due to flood risk
Property saved due to strong family fit
Suburb downgraded due to commute
School elevated due to community
```

## Memory Storage Model

Recommended tables:

```text
FamilyMemory
MemoryEvent
PreferenceEvent
DecisionJournalEntry
PropertyEvaluation
```

## FamilyMemory Fields

```text
MemoryID
FamilyID
MemoryType
Subject
Value
Confidence
Source
CreatedAt
UpdatedAt
ExpiresAt optional
```

## MemoryType Values

```text
Permanent
Preference
Learned
Session
Decision
```

## Memory Governance

The system must allow:

```text
Add memory
Update memory
Retire memory
Override memory
Explain memory source
```

## Memory Example

```text
MemoryType: Learned
Subject: CommunityPriority
Value: Family consistently prioritises strong community over prestige.
Confidence: 0.86
Source: Derived from 12 property reviews and 4 explicit comments.
```

## Implementation Requirement

Every recommendation must be able to explain which memories influenced it.

Example:

```text
This property scores highly because it aligns with three confirmed family memories:
1. Preference for modern coastal homes
2. Need for strong family community
3. Requirement for beach access within 20 minutes
```

---

# Chapter 35 – Decision Journal Framework

## Objective

Create a permanent record of property decisions so the family can see how their thinking evolves.

## Why This Matters

Relocation decisions are emotionally noisy.

Families forget why they rejected a property.

They revisit poor options.

They change their mind without noticing.

A Decision Journal creates clarity.

## Journal Entry Types

```text
PropertyReview
SuburbReview
SchoolReview
InspectionNote
FamilyDiscussion
DecisionChange
Concern
ShortlistChange
```

## DecisionJournalEntry Fields

```text
JournalEntryID
FamilyID
EntryType
RelatedPropertyID optional
RelatedSuburbID optional
RelatedSchoolID optional
Title
Summary
Decision
Reasoning
Concerns
FamilyMemberImpacts
CreatedBy
CreatedAt
```

## Decision Values

```text
Ignore
Monitor
Inspect
Prioritise
Reject
Revisit
```

## Example Entry

```text
Title: Robina family home with pool
Decision: Inspect
Reasoning: Strong community fit, good school access, pool, home office and strong lifestyle access.
Concerns: Possible road noise and slightly older interior.
FamilyMemberImpacts:
Ronnie: Strong school and community fit.
Susie: Likes layout but may dislike dated finishes.
Austin: Good parks and family area.
Mabel: Yard appears suitable.
```

## Decision Drift Detection

The system should detect when the family’s behaviour contradicts previous decisions.

Example:

```text
Family rejected Varsity Lakes due to distance from beach.
Family later saved 5 Varsity Lakes homes.
System prompt: "Your behaviour suggests Varsity Lakes may be worth reconsidering. Should we update your suburb preference?"
```

## Implementation Requirement

Every property review must create or update a Decision Journal entry.

---

# Chapter 36 – Property Evaluation Workflow

## Objective

Define the end-to-end process for evaluating a property.

## Workflow Steps

### Step 1 – Ingest Property

Capture:

```text
PropertyID
SourceURL
Address
Suburb
PriceGuide
Bedrooms
Bathrooms
CarSpaces
LandSize
PropertyType
ListingDescription
Images
Agent
ListingDate
```

### Step 2 – Validate Non-Negotiables

Check:

```text
Detached house
Pool
Home office or office potential
Air conditioning
Within budget
Within 20 minutes of Burleigh
Within 20 minutes of beach access
Low flood risk
Safe street
Strong family area
```

### Step 3 – Score Core Categories

Generate:

```text
Community Score
Lifestyle Score
School Score
Property Score
Financial Score
Risk Score
Family Fit Score
```

### Step 4 – Identify Family Impacts

Evaluate for:

```text
Ronnie
Susie
Austin
Mabel
Whole family
```

### Step 5 – Generate Recommendation

Possible outputs:

```text
Ignore
Monitor
Inspect
Prioritise Immediately
```

### Step 6 – Explain Recommendation

Every recommendation must include:

```text
Why it fits
Why it may not fit
What to verify
What the family may regret
What each family member will like
```

### Step 7 – Update Memory

Create:

```text
Preference events
Decision journal entry
Updated property status
Updated recommendation confidence
```

## Evaluation Output Template

```text
Executive Summary
Family Fit Score
Community Score
Lifestyle Score
School Score
Property Score
Financial Score
Risks
What Ronnie Will Like
What Susie Will Like
What Austin Will Like
What Mabel Will Like
What You May Regret
Recommendation
Next Action
```

## Implementation Requirement

The property evaluation workflow must be deterministic enough to build but flexible enough for AI explanation.

Scores should be structured.

Commentary should be generated.

---

# Chapter 37 – Recommendation Confidence Model

## Objective

Show how confident the system is in each recommendation.

A score alone is not enough.

A property may score 86 but have low confidence because critical information is missing.

## Confidence Inputs

```text
Completeness of property data
Availability of suburb data
Availability of school data
Flood risk clarity
Crime data clarity
Image quality
Price confidence
Preference alignment confidence
Number of confirmed family preferences used
```

## Confidence Score

Scale:

```text
0.0 to 1.0
```

Display:

```text
Low Confidence
Moderate Confidence
High Confidence
Very High Confidence
```

## Confidence Bands

```text
0.00–0.39 Low
0.40–0.64 Moderate
0.65–0.84 High
0.85–1.00 Very High
```

## Confidence Penalties

Apply penalties for:

```text
Missing price guide
No floorplan
Unclear flood risk
Poor image coverage
Unknown school catchment
Insufficient suburb data
Listing language appears exaggerated
High variance in comparable sales
```

## Example

```text
Family Fit Score: 88
Recommendation: Inspect
Confidence: 0.62 Moderate

Reason:
The property appears to strongly fit the family, but confidence is reduced because flood risk requires verification and school catchment data is incomplete.
```

## Implementation Requirement

Every recommendation must include both:

```text
Fit Score
Confidence Score
```

The system must not present low-confidence recommendations as certain.

---

# Chapter 38 – Decision Explainability Framework

## Objective

Make every recommendation understandable.

The family should never see a score without knowing why it was produced.

## Explanation Layers

### Layer 1 – Simple Explanation

Plain English summary.

Example:

```text
This looks like a strong fit because it matches your need for a modern family home, strong school access and a community-oriented suburb.
```

### Layer 2 – Category Explanation

Explain the category scores.

Example:

```text
Community scored 8.4 because the suburb has strong family density, good owner-occupier presence and positive school access.
```

### Layer 3 – Family Member Explanation

Explain how the property fits each person.

Example:

```text
Susie is likely to like the modern kitchen, pool and indoor-outdoor flow.
Ronnie is likely to value the school ecosystem and family demographic.
Austin is likely to benefit from nearby parks and local children.
Mabel has a suitable yard and nearby walking options.
```

### Layer 4 – Trade-Off Explanation

Show the compromise.

Example:

```text
The main trade-off is that the home is stronger on community and schools than daily beach access.
```

### Layer 5 – Evidence Explanation

Show what the system used.

Example:

```text
This evaluation used property listing data, suburb classification, school proximity, travel time estimates and your confirmed family preferences.
```

## Explanation Requirements

Every explanation must include:

```text
Why recommended
Why not perfect
What to verify
What may be regretted
Which family preferences were used
```

## Implementation Requirement

Do not hide behind generic phrases.

Bad:

```text
This is a good lifestyle fit.
```

Good:

```text
This is a good lifestyle fit because it is within the 20-minute Burleigh access threshold, has strong access to wellness infrastructure and remains close enough to beach access for daily use.
```

---

# Chapter 39 – Future Life Outcome Prediction

## Objective

Estimate whether a property and suburb combination is likely to improve the family’s life over a five-year horizon.

This is not a guarantee.

It is a structured prediction based on known success factors.

## Prediction Dimensions

```text
Community Belonging
Child Friendships
Parent Friendships
Lifestyle Improvement
Stress Reduction
School Fit
Home Satisfaction
Financial Comfort
Regret Risk
```

## Outcome Prediction Score

Scale:

```text
0–100
```

## Suggested Weighting

```text
Community Belonging = 20
Child Friendships = 15
Parent Friendships = 15
Lifestyle Improvement = 15
School Fit = 15
Home Satisfaction = 10
Financial Comfort = 5
Regret Risk = 5
```

## Five-Year Fit Bands

```text
90–100 Excellent probability of success
80–89 Strong probability of success
70–79 Possible fit but trade-offs need attention
60–69 Risky fit
Below 60 Poor fit
```

## Example Prediction

```text
Five-Year Fit Score: 84

This property has a strong probability of improving family life because it performs well across community, school ecosystem and home satisfaction. The main risk is whether daily beach access feels easy enough for Susie over time.
```

## Prediction Caveat

The system must always communicate uncertainty.

Recommended wording:

```text
This is a structured prediction, not a guarantee. The biggest unknowns are actual street feel, school parent community and whether the lifestyle rhythm feels natural after moving.
```

## Implementation Requirement

The Future Life Outcome Prediction must be shown separately from the Property Score.

A beautiful house can have a weak future life score.

A less impressive house can have a strong future life score.

---

# Chapter 40 – Family Decision Intelligence Engine

## Objective

Define the master engine that combines property data, suburb data, school data, lifestyle data, family memory and preference learning into an actionable recommendation.

## Engine Inputs

```text
Property Data
Suburb Data
School Data
Lifestyle Data
Crime Data
Flood Data
Travel Time Data
Family Profile
Family Memory
Preference Events
Decision Journal
User Feedback
```

## Engine Processing Steps

### Step 1 – Data Normalisation

Standardise incoming data.

### Step 2 – Non-Negotiable Filter

Remove or downgrade properties that fail hard requirements.

### Step 3 – Category Scoring

Calculate:

```text
Community Score
Lifestyle Score
School Score
Property Score
Financial Score
Risk Score
```

### Step 4 – Family Fit Calculation

Apply family weighting.

```text
Family Fit =
Community × 25%
+ Lifestyle × 20%
+ School × 20%
+ Property × 20%
+ Financial × 15%
```

### Step 5 – Individual Impact Assessment

Assess impact for:

```text
Ronnie
Susie
Austin
Mabel
```

### Step 6 – Future Life Prediction

Estimate five-year fit.

### Step 7 – Confidence Calculation

Calculate confidence based on data completeness and preference alignment.

### Step 8 – Recommendation Generation

Return:

```text
Ignore
Monitor
Inspect
Prioritise Immediately
```

### Step 9 – Explanation Generation

Create plain English reasoning.

### Step 10 – Memory Update

Update:

```text
Preference Events
Family Memory
Decision Journal
Property Status
```

## Engine Outputs

```text
Recommendation
Family Fit Score
Five-Year Fit Score
Confidence Score
Score Breakdown
Risk Flags
Family Member Commentary
Trade-Offs
What To Verify
Next Action
Memory Updates
```

## Recommendation Decision Rules

### Prioritise Immediately

Use when:

```text
Family Fit Score >= 90
Confidence >= 0.70
No critical risks
Meets all non-negotiables
Strong community and school alignment
```

### Inspect

Use when:

```text
Family Fit Score >= 80
Confidence >= 0.55
No unresolved critical risk
Strong enough to justify action
```

### Monitor

Use when:

```text
Family Fit Score >= 70
Or price/value uncertainty exists
Or property is good but not urgent
```

### Ignore

Use when:

```text
Family Fit Score < 70
Or fails non-negotiables
Or risk profile is unacceptable
Or family fit is weak
```

## Critical Override Rules

Always downgrade or reject for:

```text
High flood risk
Unsafe street
No pool
Attached dwelling
Outside budget
Poor fit for Austin’s school/community needs
Unacceptable commute to lifestyle anchors
Major road noise risk
```

## Advisor Behaviour

The system should behave like a trusted relocation advisor.

It should be:

• Direct  
• Opinionated  
• Evidence-aware  
• Family-aware  
• Clear about trade-offs  
• Honest about uncertainty

## Final Advisor Test

Every recommendation must answer:

```text
If this were my decision, based on everything I know about this family, what would I do?
```

## Implementation Requirement

The Family Decision Intelligence Engine must be implemented as a modular service so each scoring layer can evolve independently.

Recommended modules:

```text
PropertyScoringService
CommunityScoringService
LifestyleScoringService
SchoolScoringService
RiskScoringService
FamilyFitService
PreferenceLearningService
MemoryService
RecommendationService
ExplainabilityService
DecisionJournalService
```

---

# Continuity Notes From v0.1–v0.3

The core philosophy remains unchanged:

```text
Optimise for:
1. Community
2. Lifestyle
3. School ecosystem
4. Property quality
5. Financial outcome
```

Do not optimise primarily for:

```text
Prestige
Waterfront status
School rankings alone
Property features alone
Walkability alone
```

The product exists to help families choose a better life, not just a better house.

---

End of Project Bible v0.4
