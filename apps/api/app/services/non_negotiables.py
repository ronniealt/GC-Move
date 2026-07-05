from dataclasses import dataclass
from typing import Optional

from app.models.family import Family
from app.models.property import Property, PropertyFeature


@dataclass
class NonNegotiableResult:
    passed: bool
    failure_key: Optional[str] = None
    failure_reason: Optional[str] = None


# Criteria checked by keyword match against property features/description,
# rather than a direct field comparison.
_HAS_KEYWORDS = {
    "has_pool": ("swimming pool", "inground pool", "in-ground pool", "pool"),
    "has_double_garage": ("double garage", "2 car garage", "two car garage", "double lock-up garage"),
    "has_home_office": ("home office", "study", "study nook"),
}

_DRIVE_TIME_FEATURE_KEY = {
    "max_beach_drive_minutes": "beach_drive_minutes",
    "max_burleigh_drive_minutes": "burleigh_drive_minutes",
}


def check_non_negotiables(
    prop: Property,
    family: Family,
    features: list[PropertyFeature],
    school_catchment_met: Optional[dict[str, bool]] = None,
) -> NonNegotiableResult:
    """Gate a property against the family's structured must-haves.

    Reads `family.non_negotiables` (family_non_negotiables rows) instead of a
    fixed rule set — a family with none configured has nothing filtered here
    except budget. `school_catchment_met` is resolved by the caller (needs a
    School/SchoolCatchment lookup this function intentionally stays DB-free).
    """
    feature_map = {f.feature_key: f.feature_value for f in features}
    feature_keys = {f.feature_key.lower() for f in features}
    description = (prop.description_text or "").lower()

    for criterion in family.non_negotiables:
        result = _evaluate_criterion(
            criterion, prop, feature_map, feature_keys, description, school_catchment_met
        )
        if result is not None:
            return result

    if family.budget_max_aud and prop.price_range_high_aud:
        if prop.price_range_high_aud > family.budget_max_aud:
            return NonNegotiableResult(
                passed=False,
                failure_key="within_budget",
                failure_reason=(
                    f"Price ceiling ${prop.price_range_high_aud:,} exceeds "
                    f"family budget ${family.budget_max_aud:,}"
                ),
            )

    return NonNegotiableResult(passed=True)


def _evaluate_criterion(
    criterion,
    prop: Property,
    feature_map: dict,
    feature_keys: set,
    description: str,
    school_catchment_met: Optional[dict[str, bool]],
) -> Optional[NonNegotiableResult]:
    key = criterion.criterion_key

    if key == "property_type":
        if prop.property_type != criterion.value:
            return NonNegotiableResult(
                passed=False,
                failure_key="property_type",
                failure_reason=f"Property type is '{prop.property_type}', not '{criterion.value}'",
            )
        return None

    if key == "min_bedrooms":
        required = int(criterion.value)
        if prop.bedrooms is None or prop.bedrooms < required:
            have = prop.bedrooms if prop.bedrooms is not None else "unknown"
            return NonNegotiableResult(
                passed=False,
                failure_key="min_bedrooms",
                failure_reason=f"Has {have} bedrooms, needs {required}+",
            )
        return None

    if key in _HAS_KEYWORDS:
        keywords = _HAS_KEYWORDS[key]
        in_features = any(any(kw in fk for kw in keywords) for fk in feature_keys)
        in_description = any(kw in description for kw in keywords)
        if not in_features and not in_description:
            return NonNegotiableResult(
                passed=False,
                failure_key=key,
                failure_reason=f"No {criterion.label or key} detected in property features or description",
            )
        return None

    if key in _DRIVE_TIME_FEATURE_KEY:
        feature_key = _DRIVE_TIME_FEATURE_KEY[key]
        val = feature_map.get(feature_key)
        if val is not None:
            try:
                limit = float(criterion.value)
                if float(val) > limit:
                    label = feature_key.replace("_", " ").title()
                    return NonNegotiableResult(
                        passed=False,
                        failure_key=key,
                        failure_reason=f"{label} {int(float(val))} min exceeds {int(limit)}-minute limit",
                    )
            except (ValueError, TypeError):
                pass
        return None

    if key == "school_catchment":
        met = (school_catchment_met or {}).get(criterion.value)
        if met is False:
            return NonNegotiableResult(
                passed=False,
                failure_key="school_catchment",
                failure_reason=f"Not in the {criterion.value} catchment",
            )
        return None

    return None
