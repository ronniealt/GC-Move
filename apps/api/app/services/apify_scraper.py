import asyncio
from typing import Optional

from apify_client import ApifyClient
from pydantic import BaseModel

from app.config import settings


class PropertyExtractionError(Exception):
    pass


class ExtractedPropertyData(BaseModel):
    address_street: str
    address_suburb: str
    address_postcode: str
    address_state: str = "QLD"
    listing_price_aud: Optional[int] = None
    price_range_low_aud: Optional[int] = None
    price_range_high_aud: Optional[int] = None
    price_is_range: bool = False
    bedrooms: Optional[int] = None
    bathrooms: Optional[float] = None
    car_spaces: Optional[int] = None
    land_area_sqm: Optional[int] = None
    house_area_sqm: Optional[int] = None
    property_type: str = "house"
    description: str = ""
    features: list[str] = []
    image_urls: list[str] = []
    agent_name: Optional[str] = None
    agency_name: Optional[str] = None
    source_platform: str = "realestate"
    source_listing_id: Optional[str] = None
    source_url: str
    raw_data: dict = {}


def _run_apify_sync(url: str) -> dict:
    client = ApifyClient(settings.APIFY_API_TOKEN)
    actor_id = (
        settings.APIFY_REA_ACTOR_ID
        if "realestate.com.au" in url
        else settings.APIFY_DOMAIN_ACTOR_ID
    )
    run = client.actor(actor_id).call(
        run_input={"startUrls": [{"url": url}], "maxItems": 1},
        timeout_secs=60,
    )
    if not run or not run.get("defaultDatasetId"):
        raise PropertyExtractionError(f"Apify run failed for: {url}")
    items = list(client.dataset(run["defaultDatasetId"]).iterate_items())
    if not items:
        raise PropertyExtractionError(f"Apify returned no data for: {url}")
    return items[0]


async def fetch_property_via_apify(url: str) -> dict:
    return await asyncio.to_thread(_run_apify_sync, url)


def _extract_price(raw: dict) -> tuple[Optional[int], Optional[int], Optional[int], bool]:
    if raw.get("listingPrice"):
        try:
            return int(raw["listingPrice"]), None, None, False
        except (ValueError, TypeError):
            pass
    if raw.get("priceFrom") and raw.get("priceTo"):
        try:
            return None, int(raw["priceFrom"]), int(raw["priceTo"]), True
        except (ValueError, TypeError):
            pass
    return None, None, None, False


def _to_int(val) -> Optional[int]:
    if val is None:
        return None
    try:
        return int(val)
    except (ValueError, TypeError):
        return None


def _to_float(val) -> Optional[float]:
    if val is None:
        return None
    try:
        return float(val)
    except (ValueError, TypeError):
        return None


def _normalise_property_type(raw_type: str) -> str:
    t = raw_type.lower()
    if any(k in t for k in ("house", "home", "villa", "cottage")):
        return "house"
    if any(k in t for k in ("townhouse", "town")):
        return "townhouse"
    if any(k in t for k in ("unit", "apartment", "flat", "studio")):
        return "unit"
    if any(k in t for k in ("acreage", "rural", "farm", "land")):
        return "acreage"
    return "other"


def _extract_images(raw: dict) -> list[str]:
    images = raw.get("images") or raw.get("photos") or raw.get("imageUrls") or []
    if not images:
        return []
    if isinstance(images[0], dict):
        return [img.get("url") or img.get("src") or "" for img in images if isinstance(img, dict)]
    return [str(img) for img in images if img]


def _extract_features(raw: dict) -> list[str]:
    feats = raw.get("features") or raw.get("propertyFeatures") or raw.get("listingFeatures") or []
    if not feats:
        return []
    if feats and isinstance(feats[0], dict):
        return [f.get("name") or f.get("label") or str(f) for f in feats if isinstance(f, dict)]
    return [str(f) for f in feats if f]


def map_apify_to_property(raw: dict, url: str) -> ExtractedPropertyData:
    platform = "realestate" if "realestate.com.au" in url else "domain"

    address = (
        raw.get("address")
        or raw.get("displayableAddress")
        or raw.get("streetAddress")
        or ""
    )
    suburb = raw.get("suburb") or raw.get("suburbName") or raw.get("locality") or ""
    postcode = str(raw.get("postcode") or raw.get("postCode") or "")[:4]
    state = raw.get("state") or "QLD"

    listing_price, price_low, price_high, price_is_range = _extract_price(raw)

    raw_type = raw.get("propertyType") or raw.get("type") or raw.get("category") or "house"
    property_type = _normalise_property_type(str(raw_type))

    return ExtractedPropertyData(
        address_street=address,
        address_suburb=suburb,
        address_postcode=postcode,
        address_state=state,
        listing_price_aud=listing_price,
        price_range_low_aud=price_low,
        price_range_high_aud=price_high,
        price_is_range=price_is_range,
        bedrooms=_to_int(raw.get("bedrooms") or raw.get("beds")),
        bathrooms=_to_float(raw.get("bathrooms") or raw.get("baths")),
        car_spaces=_to_int(raw.get("carSpaces") or raw.get("parking") or raw.get("garages")),
        land_area_sqm=_to_int(raw.get("landArea") or raw.get("landSize") or raw.get("lotSize")),
        house_area_sqm=_to_int(raw.get("buildingArea") or raw.get("floorArea") or raw.get("houseArea")),
        property_type=property_type,
        description=raw.get("description") or raw.get("listingDescription") or "",
        features=_extract_features(raw),
        image_urls=_extract_images(raw)[:20],
        agent_name=raw.get("agentName") or raw.get("advertiserName"),
        agency_name=raw.get("agencyName"),
        source_platform=platform,
        source_listing_id=str(raw.get("id") or raw.get("listingId") or raw.get("propertyId") or ""),
        source_url=url,
        raw_data=raw,
    )
