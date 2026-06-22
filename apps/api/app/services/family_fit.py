from app.models.family import Family

NEUTRAL_FINANCIAL = 5.0


def calculate_family_fit(
    community: float,
    lifestyle: float,
    school: float,
    property_score: float,
    financial: float,
    family: Family,
) -> float:
    return round(
        community * float(family.weight_community)
        + lifestyle * float(family.weight_lifestyle)
        + school * float(family.weight_school)
        + property_score * float(family.weight_property)
        + financial * float(family.weight_financial),
        1,
    )


def calculate_five_year_fit(
    community: float,
    lifestyle: float,
    school: float,
    property_score: float,
    financial: float,
    risk_score: float,
) -> float:
    # community maps to community_belonging (0.20) + parent_friendships (0.15)
    # school maps to school_fit (0.15) + child_friendships (0.15)
    score = (
        community * 0.35
        + school * 0.30
        + lifestyle * 0.15
        + property_score * 0.10
        + financial * 0.05
        + risk_score * 0.05
    )
    return round(min(max(score, 0.0), 10.0), 1)


def determine_recommendation(
    family_fit: float,
    confidence: float,
    has_critical_risk: bool,
    meets_non_negotiables: bool,
) -> str:
    if not meets_non_negotiables or has_critical_risk:
        return "ignore"
    if family_fit >= 9.0 and confidence >= 0.70:
        return "prioritise_immediately"
    if family_fit >= 8.0 and confidence >= 0.55:
        return "inspect"
    if family_fit >= 7.0:
        return "monitor"
    return "ignore"


RECOMMENDATION_LABELS = {
    "prioritise_immediately": "Prioritise Immediately",
    "inspect": "Inspect",
    "monitor": "Monitor",
    "ignore": "Ignore",
}
