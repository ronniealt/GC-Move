import uuid as _uuid

import sentry_sdk
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.database import AsyncSessionLocal
from app.models.location import Suburb
from app.models.property import Property, PropertyFeature, PropertyImage
from app.services.apify_scraper import (
    ExtractedPropertyData,
    PropertyExtractionError,
    fetch_property_via_apify,
    map_apify_to_property,
)
from app.services.qualitative_enrichment import enrich_qualitative


async def ingest_property(property_id: str, url: str, family_id: str) -> None:
    try:
        async with AsyncSessionLocal() as db:
            await _do_ingest(property_id, url, family_id, db)
    except Exception as e:
        sentry_sdk.capture_exception(e)
        async with AsyncSessionLocal() as db:
            await _mark_failed(property_id, db)


async def _do_ingest(property_id: str, url: str, family_id: str, db) -> None:
    pid = _uuid.UUID(property_id)
    fid = _uuid.UUID(family_id)

    result = await db.execute(
        select(Property).where(
            Property.id == pid,
            Property.family_id == fid,
        )
    )
    prop = result.scalar_one_or_none()
    if prop is None:
        return

    raw = await fetch_property_via_apify(url)
    data = map_apify_to_property(raw, url)

    _apply_extracted_data(prop, data)

    suburb = await _resolve_suburb(data.address_suburb, db)
    if suburb:
        prop.suburb_id = suburb.id

    for feat in _build_features(data, fid, pid):
        db.add(feat)

    for img in _build_images(data, fid, pid):
        db.add(img)

    await db.flush()

    scores = await enrich_qualitative(data.description, data.features)

    qualitative = {
        "modernity": scores.modernity,
        "design_quality": scores.design_quality,
        "indoor_outdoor_flow": scores.indoor_outdoor_flow,
        "home_office_suitability": scores.home_office_suitability,
        "entertaining_space": scores.entertaining_space,
        "privacy": scores.privacy,
    }
    for key, val in qualitative.items():
        if val is not None:
            db.add(PropertyFeature(
                family_id=fid,
                property_id=pid,
                feature_key=key,
                feature_value=str(val),
                feature_type="numeric",
                source="inferred",
                confidence=0.75,
            ))

    prop.data_quality_score = _calculate_quality_score(prop, data)
    prop.extraction_confidence = round(prop.data_quality_score / 100, 2)
    prop.status = "evaluated"
    await db.commit()


def _apply_extracted_data(prop: Property, data: ExtractedPropertyData) -> None:
    prop.address_street = data.address_street or prop.address_street
    prop.address_suburb = data.address_suburb or prop.address_suburb
    prop.address_postcode = data.address_postcode or prop.address_postcode
    prop.address_state = data.address_state
    prop.property_type = data.property_type
    prop.bedrooms = data.bedrooms
    prop.bathrooms = data.bathrooms
    prop.car_spaces = data.car_spaces
    prop.land_area_sqm = data.land_area_sqm
    prop.house_area_sqm = data.house_area_sqm
    prop.listing_price_aud = data.listing_price_aud
    prop.price_range_low_aud = data.price_range_low_aud
    prop.price_range_high_aud = data.price_range_high_aud
    prop.price_is_range = data.price_is_range
    prop.description_text = data.description
    prop.agent_name = data.agent_name
    prop.agency_name = data.agency_name
    prop.source_platform = data.source_platform
    prop.source_listing_id = data.source_listing_id or ""


async def _resolve_suburb(suburb_name: str, db) -> Suburb | None:
    if not suburb_name or suburb_name == "Pending":
        return None
    result = await db.execute(
        select(Suburb).where(Suburb.name.ilike(suburb_name.strip()))
    )
    return result.scalar_one_or_none()


def _build_features(
    data: ExtractedPropertyData, family_id: _uuid.UUID, property_id: _uuid.UUID
) -> list[PropertyFeature]:
    seen: set[str] = set()
    features = []
    for feat_str in data.features:
        feat_str = feat_str.strip()
        if not feat_str:
            continue
        key = feat_str.lower().replace(" ", "_")[:100]
        if key in seen:
            continue
        seen.add(key)
        features.append(PropertyFeature(
            family_id=family_id,
            property_id=property_id,
            feature_key=key,
            feature_value=feat_str[:255],
            feature_type="boolean",
            source="extracted",
            confidence=0.90,
        ))
    return features


def _build_images(
    data: ExtractedPropertyData, family_id: _uuid.UUID, property_id: _uuid.UUID
) -> list[PropertyImage]:
    return [
        PropertyImage(
            family_id=family_id,
            property_id=property_id,
            image_url=url,
            image_order=i,
            image_type="listing",
        )
        for i, url in enumerate(data.image_urls)
        if url
    ]


def _calculate_quality_score(prop: Property, data: ExtractedPropertyData) -> int:
    checks = [
        bool(prop.bedrooms),
        bool(prop.bathrooms),
        bool(prop.property_type and prop.property_type != "house"),
        bool(prop.land_area_sqm),
        bool(prop.description_text and len(prop.description_text) > 50),
        bool(data.image_urls),
        bool(prop.listing_price_aud or prop.price_range_low_aud),
    ]
    return int((sum(checks) / len(checks)) * 100)


async def _mark_failed(property_id: str, db) -> None:
    try:
        pid = _uuid.UUID(property_id)
        result = await db.execute(select(Property).where(Property.id == pid))
        prop = result.scalar_one_or_none()
        if prop:
            prop.status = "failed"
            await db.commit()
    except Exception as e:
        sentry_sdk.capture_exception(e)
