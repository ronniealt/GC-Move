from dataclasses import dataclass
from typing import Optional

from app.models.location import SuburbMetric


@dataclass
class CommunityScoreResult:
    community_score: float
    owner_occupier: float
    family_density: float
    educational_attainment: float
    median_income: float
    crime: float
    community_engagement: float
    confidence: float


def calculate_community_score(metric: Optional[SuburbMetric]) -> CommunityScoreResult:
    if metric is None:
        return CommunityScoreResult(
            community_score=5.0,
            owner_occupier=5.0,
            family_density=5.0,
            educational_attainment=5.0,
            median_income=5.0,
            crime=5.0,
            community_engagement=5.0,
            confidence=0.0,
        )

    present = [
        metric.owner_occupier_rate is not None,
        metric.family_density_pct is not None,
        metric.educational_attainment_pct is not None,
        metric.median_weekly_household_income_aud is not None,
        metric.crime_index is not None,
        metric.community_engagement_score is not None,
    ]
    confidence = round(sum(present) / len(present), 2)

    oo = _norm(metric.owner_occupier_rate, 0.5, 1.0)
    fd = _norm(metric.family_density_pct, 0.2, 0.6)
    ea = _norm(metric.educational_attainment_pct, 0.3, 0.8)
    mi = _norm(metric.median_weekly_household_income_aud, 60000, 150000)
    crime_val = float(metric.crime_index) if metric.crime_index is not None else 5.0
    cr = _norm(10.0 - crime_val, 0.0, 10.0)
    ce = _norm(metric.community_engagement_score, 0.0, 10.0)

    raw = (
        oo * 0.30 +
        fd * 0.20 +
        ea * 0.15 +
        mi * 0.15 +
        cr * 0.15 +
        ce * 0.05
    ) * 10

    return CommunityScoreResult(
        community_score=round(min(max(raw, 0.0), 10.0), 1),
        owner_occupier=round(oo * 10, 1),
        family_density=round(fd * 10, 1),
        educational_attainment=round(ea * 10, 1),
        median_income=round(mi * 10, 1),
        crime=round(cr * 10, 1),
        community_engagement=round(ce * 10, 1),
        confidence=confidence,
    )


def _norm(val, lo, hi) -> float:
    if val is None:
        return 0.5
    try:
        v = float(val)
    except (ValueError, TypeError):
        return 0.5
    if hi == lo:
        return 0.5
    return max(0.0, min(1.0, (v - lo) / (hi - lo)))
