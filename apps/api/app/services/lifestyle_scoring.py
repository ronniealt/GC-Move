from dataclasses import dataclass
from typing import Optional

from app.models.location import SuburbLifestyleAsset
from app.models.property import PropertyFeature


@dataclass
class LifestyleScoreResult:
    lifestyle_score: float
    burleigh_access: float
    beach_access: float
    wellness: float
    cafe_dining: float
    outdoor_recreation: float
    shopping: float
    confidence: float


def calculate_lifestyle_score(
    features: list[PropertyFeature],
    lifestyle: Optional[SuburbLifestyleAsset],
) -> LifestyleScoreResult:
    feature_map = {f.feature_key: f.feature_value for f in features}

    burleigh_mins = _get_float(feature_map, "burleigh_drive_minutes")
    beach_mins = _get_float(feature_map, "beach_drive_minutes")

    if burleigh_mins is None and lifestyle is not None and lifestyle.burleigh_drive_minutes is not None:
        burleigh_mins = float(lifestyle.burleigh_drive_minutes)
    if beach_mins is None and lifestyle is not None and lifestyle.beach_access_minutes is not None:
        beach_mins = float(lifestyle.beach_access_minutes)

    burleigh_score = _score_travel(burleigh_mins, ideal=10, max_ok=20)
    beach_score = _score_travel(beach_mins, ideal=5, max_ok=15)

    if lifestyle is not None:
        cafe = _norm(lifestyle.cafe_restaurant_count, 0, 15)
        wellness = _norm(
            (lifestyle.gym_fitness_count or 0) + (lifestyle.pilates_yoga_count or 0),
            0, 20,
        )
        outdoor = _norm(lifestyle.park_reserve_count, 0, 10)
        shopping = _norm(lifestyle.shopping_centre_count, 0, 10)
        data_confidence = 1.0
    else:
        cafe = wellness = outdoor = shopping = 0.5
        data_confidence = 0.3

    travel_confidence = 0.0 if burleigh_mins is None and beach_mins is None else 1.0
    confidence = round((data_confidence + travel_confidence) / 2, 2)

    raw = (
        burleigh_score * 0.25 +
        beach_score * 0.20 +
        wellness * 0.20 +
        cafe * 0.15 +
        outdoor * 0.10 +
        shopping * 0.10
    ) * 10

    return LifestyleScoreResult(
        lifestyle_score=round(min(max(raw, 0.0), 10.0), 1),
        burleigh_access=round(burleigh_score * 10, 1),
        beach_access=round(beach_score * 10, 1),
        wellness=round(wellness * 10, 1),
        cafe_dining=round(cafe * 10, 1),
        outdoor_recreation=round(outdoor * 10, 1),
        shopping=round(shopping * 10, 1),
        confidence=confidence,
    )


def _score_travel(minutes: Optional[float], ideal: int, max_ok: int) -> float:
    if minutes is None:
        return 0.5
    if minutes <= ideal:
        return 1.0
    if minutes <= max_ok:
        return 1.0 - ((minutes - ideal) / (max_ok - ideal)) * 0.5
    return max(0.0, 1.0 - ((minutes - max_ok) / 10) * 0.5)


def _get_float(d: dict, key: str) -> Optional[float]:
    val = d.get(key)
    if val is None:
        return None
    try:
        return float(val)
    except (ValueError, TypeError):
        return None


def _norm(val, lo: int, hi: int) -> float:
    if val is None:
        return 0.5
    try:
        v = float(val)
    except (ValueError, TypeError):
        return 0.5
    if hi == lo:
        return 0.5
    return max(0.0, min(1.0, (v - lo) / (hi - lo)))
