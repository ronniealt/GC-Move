from dataclasses import dataclass
from typing import Optional

from app.models.property import PropertyFeature

_QUALITATIVE_FIELDS = [
    ("modernity", 0.20),
    ("design_quality", 0.15),
    ("indoor_outdoor_flow", 0.15),
    ("entertaining_space", 0.10),
    ("privacy", 0.10),
]
_QUALITATIVE_TOTAL_WEIGHT = sum(w for _, w in _QUALITATIVE_FIELDS)  # 0.70


@dataclass
class PropertyScoreResult:
    property_score: float
    modernity: float
    design_quality: float
    indoor_outdoor_flow: float
    pool: float
    home_office: float
    entertaining_space: float
    privacy: float
    block_utility: float
    confidence: float


def calculate_property_score(
    features: list[PropertyFeature],
    land_area_sqm: Optional[int],
) -> PropertyScoreResult:
    feature_map = {f.feature_key: f.feature_value for f in features}
    feature_keys = {f.feature_key.lower() for f in features}

    def _q(key: str) -> Optional[float]:
        val = feature_map.get(key)
        if val is None:
            return None
        try:
            return float(val)
        except (ValueError, TypeError):
            return None

    qualitative_scores = {name: _q(name) for name, _ in _QUALITATIVE_FIELDS}

    present = [(name, s, w) for (name, w) in _QUALITATIVE_FIELDS for s in [qualitative_scores[name]] if s is not None]
    present_weight = sum(w for _, _, w in present)

    if present and present_weight > 0:
        scale = _QUALITATIVE_TOTAL_WEIGHT / present_weight
        q_contribution = sum(s * w * scale for _, s, w in present)
    else:
        q_contribution = 5.0 * _QUALITATIVE_TOTAL_WEIGHT

    has_pool = any("pool" in k for k in feature_keys)
    pool_score = 10.0 if has_pool else 0.0

    has_office = any("office" in k or "study" in k for k in feature_keys)
    office_score = 10.0 if has_office else 3.0

    block_util = _norm_land(land_area_sqm)

    det_contribution = pool_score * 0.10 + office_score * 0.10 + block_util * 0.10

    score = round(min(max(q_contribution + det_contribution, 0.0), 10.0), 1)
    confidence = round(min(1.0, 0.5 + len(present) * 0.10), 2)

    return PropertyScoreResult(
        property_score=score,
        modernity=qualitative_scores.get("modernity") or 5.0,
        design_quality=qualitative_scores.get("design_quality") or 5.0,
        indoor_outdoor_flow=qualitative_scores.get("indoor_outdoor_flow") or 5.0,
        pool=pool_score,
        home_office=office_score,
        entertaining_space=qualitative_scores.get("entertaining_space") or 5.0,
        privacy=qualitative_scores.get("privacy") or 5.0,
        block_utility=block_util,
        confidence=confidence,
    )


def _norm_land(sqm: Optional[int]) -> float:
    if sqm is None:
        return 5.0
    return round(max(0.0, min(10.0, (sqm - 300) / (1500 - 300) * 10)), 1)
