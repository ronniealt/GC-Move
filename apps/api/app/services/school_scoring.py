import math
import uuid as _uuid
from dataclasses import dataclass, field
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.location import School, SchoolCatchment, SchoolMetric

PREFERRED_SCHOOLS = {"Somerset College", "All Saints Anglican School"}
PREFERRED_BONUS = 0.5


@dataclass
class SchoolScoreResult:
    school_score: float
    wellbeing: float
    parent_community: float
    academic: float
    commute: float
    extracurricular: float
    pathway: float
    matched_schools: list[str] = field(default_factory=list)
    confidence: float = 0.3


async def calculate_school_score(
    suburb_id: Optional[_uuid.UUID],
    prop_lat: Optional[float],
    prop_lng: Optional[float],
    db: AsyncSession,
) -> SchoolScoreResult:
    schools: list[School] = []

    if suburb_id is not None:
        result = await db.execute(
            select(School)
            .join(SchoolCatchment, School.id == SchoolCatchment.school_id)
            .where(SchoolCatchment.suburb_id == suburb_id)
            .where(School.is_active == True)
            .options(selectinload(School.metrics))
        )
        schools = list(result.scalars().unique().all())

    if not schools and prop_lat is not None and prop_lng is not None:
        all_result = await db.execute(
            select(School)
            .where(School.is_active == True)
            .options(selectinload(School.metrics))
        )
        all_schools = list(all_result.scalars().all())
        schools = [
            s for s in all_schools
            if s.latitude is not None
            and s.longitude is not None
            and _haversine_km(prop_lat, prop_lng, float(s.latitude), float(s.longitude)) <= 20.0
        ]

    if not schools:
        return SchoolScoreResult(
            school_score=3.0,
            wellbeing=3.0,
            parent_community=3.0,
            academic=3.0,
            commute=3.0,
            extracurricular=3.0,
            pathway=3.0,
            matched_schools=[],
            confidence=0.3,
        )

    best_score = -1.0
    best_metric: Optional[SchoolMetric] = None
    has_preferred = any(s.name in PREFERRED_SCHOOLS for s in schools)

    for school in schools:
        m: Optional[SchoolMetric] = school.metrics
        if m is None:
            continue
        score = _score_school(m)
        if score > best_score:
            best_score = score
            best_metric = m

    if best_metric is None:
        return SchoolScoreResult(
            school_score=4.0,
            wellbeing=4.0,
            parent_community=4.0,
            academic=4.0,
            commute=4.0,
            extracurricular=4.0,
            pathway=4.0,
            matched_schools=[s.name for s in schools],
            confidence=0.4,
        )

    if has_preferred:
        best_score = min(10.0, best_score + PREFERRED_BONUS)

    m = best_metric
    return SchoolScoreResult(
        school_score=round(best_score, 1),
        wellbeing=round(float(m.wellbeing_score or 5.0), 1),
        parent_community=round(float(m.parent_community_score or 5.0), 1),
        academic=round(float(m.academic_outcomes_score or 5.0), 1),
        commute=round(float(m.commute_score or 5.0), 1),
        extracurricular=round(float(m.extracurricular_score or 5.0), 1),
        pathway=round(float(m.pathway_score or 5.0), 1),
        matched_schools=[s.name for s in schools],
        confidence=0.8,
    )


def _score_school(m: SchoolMetric) -> float:
    return round(
        float(m.wellbeing_score or 5.0) * 0.25
        + float(m.parent_community_score or 5.0) * 0.20
        + float(m.academic_outcomes_score or 5.0) * 0.20
        + float(m.commute_score or 5.0) * 0.15
        + float(m.extracurricular_score or 5.0) * 0.10
        + float(m.pathway_score or 5.0) * 0.10,
        1,
    )


def _haversine_km(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    R = 6371.0
    dlat = math.radians(lat2 - lat1)
    dlng = math.radians(lng2 - lng1)
    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(math.radians(lat1))
        * math.cos(math.radians(lat2))
        * math.sin(dlng / 2) ** 2
    )
    return R * 2 * math.asin(math.sqrt(min(1.0, a)))
