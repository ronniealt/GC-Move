# Gold Coast Move OS Project Bible v0.5

## Volume 5 – Data Architecture & Platform Model

# Chapter 41 – Core Domain Model

## Objective

Define the primary entities that exist within the platform.

## Core Entities

```text
Family
FamilyMember
Property
Suburb
School
PropertyEvaluation
PreferenceEvent
FamilyMemory
DecisionJournalEntry
Recommendation
Inspection
MarketSnapshot
```

## Relationship Summary

```text
Family -> many FamilyMembers
Family -> many PreferenceEvents
Family -> many PropertyEvaluations
Family -> many Recommendations

Property -> one Suburb
Property -> many Evaluations

Suburb -> many Properties
Suburb -> many Schools

Recommendation -> generated from:
Property
Suburb
School Ecosystem
Family Profile
Family Memory
```

---

# Chapter 42 – Database Architecture

## Recommended Architecture

```text
PostgreSQL
```

## Logical Domains

### Family Domain

```text
Families
FamilyMembers
FamilyPreferences
FamilyMemory
```

### Property Domain

```text
Properties
PropertyImages
PropertyFeatures
PropertyHistory
```

### Location Domain

```text
Suburbs
Schools
LifestyleAssets
```

### Intelligence Domain

```text
PropertyEvaluations
Recommendations
DecisionJournal
PreferenceEvents
```

---

# Chapter 43 – Family Tables

## Families

```text
FamilyID PK
FamilyName
CurrentLocation
TargetRegion
BudgetMin
BudgetMax
MoveTimeframe
CreatedAt
UpdatedAt
```

## FamilyMembers

```text
FamilyMemberID PK
FamilyID FK
Name
Role
Age
PriorityProfile
CreatedAt
UpdatedAt
```

## FamilyPreferences

```text
PreferenceID PK
FamilyID FK
Attribute
Weight
Confidence
Status
UpdatedAt
```

---

# Chapter 44 – Property Data Model

## Properties

```text
PropertyID PK
ExternalID
Address
SuburbID
PriceGuide
Bedrooms
Bathrooms
CarSpaces
LandSize
PropertyType
ListingStatus
SourceURL
CreatedAt
UpdatedAt
```

## PropertyFeatures

```text
FeatureID PK
PropertyID FK
FeatureName
FeatureValue
```

Examples:

```text
Pool
Office
AirConditioning
Solar
GymSpace
MediaRoom
```

---

# Chapter 45 – Suburb Intelligence Model

## Suburbs

```text
SuburbID PK
Name
State
Postcode
Population
OwnerOccupierRate
MedianIncome
CrimeIndex
FamilyDensity
CommunityScore
LifestyleScore
UpdatedAt
```

## SuburbMetrics

```text
MetricID PK
SuburbID FK
MetricName
MetricValue
Source
UpdatedAt
```

---

# Chapter 46 – School Intelligence Model

## Schools

```text
SchoolID PK
Name
Type
SuburbID
SchoolScore
WellbeingScore
AcademicScore
CommunityScore
CommuteScore
UpdatedAt
```

## SchoolCatchments

```text
CatchmentID PK
SchoolID FK
SuburbID FK
```

---

# Chapter 47 – Family Memory Data Model

## FamilyMemory

```text
MemoryID PK
FamilyID FK
MemoryType
Subject
Value
Confidence
Source
CreatedAt
UpdatedAt
```

## MemoryEvent

```text
MemoryEventID PK
MemoryID FK
Action
OldValue
NewValue
Timestamp
```

Actions:

```text
Create
Update
Retire
Override
```

---

# Chapter 48 – Preference Event Model

## PreferenceEvents

```text
PreferenceEventID PK
FamilyID FK
PropertyID nullable
SuburbID nullable
SchoolID nullable
Attribute
Sentiment
Strength
Source
EvidenceText
CreatedAt
```

## Event Examples

```text
SavedProperty
RejectedProperty
Comment
InspectionFeedback
ManualPreference
AIInference
```

---

# Chapter 49 – Recommendation Data Model

## Recommendations

```text
RecommendationID PK
FamilyID FK
PropertyID FK
RecommendationType
FamilyFitScore
ConfidenceScore
FiveYearFitScore
CreatedAt
```

## Recommendation Types

```text
Ignore
Monitor
Inspect
PrioritiseImmediately
```

## RecommendationExplanation

```text
ExplanationID PK
RecommendationID FK
Summary
Strengths
Risks
TradeOffs
NextAction
```

---

# Chapter 50 – Data Governance & Auditability

## Principle

Every recommendation must be traceable.

## Audit Requirements

The system must be able to answer:

```text
Why was this property recommended?
Which preferences were used?
Which memories were used?
Which scores were used?
Who changed a preference?
When was it changed?
```

## Audit Tables

```text
AuditLog
MemoryEvent
PreferenceEvent
RecommendationHistory
```

## Transparency Rule

No recommendation should exist without:

```text
Score breakdown
Supporting evidence
Explanation
Confidence level
Timestamp
```

---

End of Project Bible v0.5
