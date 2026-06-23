from dataclasses import dataclass
from typing import Optional

from app.models.family import Family
from app.models.property import Property, PropertyFeature


@dataclass
class NonNegotiableResult:
    passed: bool
    failure_key: Optional[str] = None
    failure_reason: Optional[str] = None


def check_non_negotiables(
    prop: Property,
    family: Family,
    features: list[PropertyFeature],
) -> NonNegotiableResult:
    if prop.property_type != "house":
        return NonNegotiableResult(
            passed=False,
            failure_key="property_type",
            failure_reason=f"Property type is '{prop.property_type}', not 'house'",
        )

    feature_keys = {f.feature_key.lower() for f in features}
    description = (prop.description_text or "").lower()

    pool_in_features = any("pool" in k for k in feature_keys)
    pool_in_description = any(
        kw in description for kw in ("swimming pool", "inground pool", "in-ground pool", "pool")
    )

    if not pool_in_features and not pool_in_description:
        return NonNegotiableResult(
            passed=False,
            failure_key="has_pool",
            failure_reason="No pool detected in property features or description",
        )

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

    feature_map = {f.feature_key: f.feature_value for f in features}

    burleigh_val = feature_map.get("burleigh_drive_minutes")
    if burleigh_val is not None:
        try:
            if float(burleigh_val) > 20:
                return NonNegotiableResult(
                    passed=False,
                    failure_key="burleigh_access",
                    failure_reason=f"Burleigh drive time {int(float(burleigh_val))} min exceeds 20-minute limit",
                )
        except (ValueError, TypeError):
            pass

    beach_val = feature_map.get("beach_drive_minutes")
    if beach_val is not None:
        try:
            if float(beach_val) > 20:
                return NonNegotiableResult(
                    passed=False,
                    failure_key="beach_access",
                    failure_reason=f"Beach drive time {int(float(beach_val))} min exceeds 20-minute limit",
                )
        except (ValueError, TypeError):
            pass

    return NonNegotiableResult(passed=True)
