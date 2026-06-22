from dataclasses import dataclass, field
from typing import Optional

from app.models.family import Family
from app.models.location import SuburbMetric
from app.models.property import Property, PropertyFeature

_DEDUCTIONS = {
    "critical": 3.0,
    "high": 2.0,
    "moderate": 1.0,
    "low": 0.3,
}


@dataclass
class Risk:
    category: str
    level: str  # "low" | "moderate" | "high" | "critical"
    description: str


@dataclass
class RiskResult:
    risks: list[Risk] = field(default_factory=list)
    has_critical_risk: bool = False
    risk_score: float = 10.0


def calculate_risk_score(
    prop: Property,
    metric: Optional[SuburbMetric],
    features: list[PropertyFeature],
    family: Family,
) -> RiskResult:
    risks: list[Risk] = []
    feature_keys = {f.feature_key.lower() for f in features}
    feature_map = {f.feature_key: f.feature_value for f in features}

    if prop.flood_risk_category == "high":
        risks.append(Risk(
            category="flood",
            level="critical",
            description="Property is in a high flood risk zone",
        ))

    if prop.property_type != "house":
        risks.append(Risk(
            category="property_type",
            level="critical",
            description=f"Property type is '{prop.property_type}', not a standalone house",
        ))

    if not any("pool" in k for k in feature_keys):
        risks.append(Risk(
            category="no_pool",
            level="critical",
            description="No pool detected — fails family non-negotiable",
        ))

    burleigh_val = feature_map.get("burleigh_drive_minutes")
    if burleigh_val is not None:
        try:
            mins = float(burleigh_val)
            if mins > 25:
                risks.append(Risk(
                    category="burleigh_access",
                    level="moderate",
                    description=f"Burleigh Heads is {int(mins)} min drive — over 25-min threshold",
                ))
        except (ValueError, TypeError):
            pass

    beach_val = feature_map.get("beach_drive_minutes")
    if beach_val is not None:
        try:
            mins = float(beach_val)
            if mins > 25:
                risks.append(Risk(
                    category="beach_access",
                    level="moderate",
                    description=f"Nearest beach is {int(mins)} min drive — over 25-min threshold",
                ))
        except (ValueError, TypeError):
            pass

    if metric is not None and metric.crime_index is not None:
        ci = float(metric.crime_index)
        if ci > 7:
            risks.append(Risk(
                category="crime",
                level="high",
                description=f"Suburb crime index {ci:.1f}/10 — elevated",
            ))
        elif ci > 5:
            risks.append(Risk(
                category="crime",
                level="moderate",
                description=f"Suburb crime index {ci:.1f}/10 — moderate concern",
            ))

    if family.budget_max_aud and prop.price_range_high_aud:
        if prop.price_range_high_aud > family.budget_max_aud:
            risks.append(Risk(
                category="outside_budget",
                level="critical",
                description=(
                    f"Price ceiling ${prop.price_range_high_aud:,} exceeds "
                    f"family budget ${family.budget_max_aud:,}"
                ),
            ))

    has_critical = any(r.level == "critical" for r in risks)
    deduction = sum(_DEDUCTIONS.get(r.level, 0.0) for r in risks)

    return RiskResult(
        risks=risks,
        has_critical_risk=has_critical,
        risk_score=round(max(0.0, 10.0 - deduction), 1),
    )
