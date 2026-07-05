import asyncio
import logging
from decimal import Decimal
from typing import Optional

from apify_client import ApifyClient
from pydantic import BaseModel

from app.config import settings

logger = logging.getLogger(__name__)


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
    logger.info("Starting Apify run: actor=%s url=%s", actor_id, url)
    run = client.actor(actor_id).call(
        run_input={
            "startUrls": [url],
            "maxItems": 1,
            "flattenOutput": True,
            "enrichEmails": False,
            "includeSurroundingSuburbs": True,
            "proxy": {"useApifyProxy": True, "apifyProxyGroups": ["RESIDENTIAL"]},
        },
        max_items=1,
        max_total_charge_usd=Decimal(str(settings.APIFY_DETAIL_MAX_USD_PER_CALL)),
        timeout_secs=600,
    )
    dataset_id = run.get("defaultDatasetId") if run else None
    run_status = run.get("status") if run else None
    logger.info("Apify run finished: status=%s dataset=%s", run_status, dataset_id)
    if not run or not dataset_id:
        raise PropertyExtractionError(f"Apify run failed (no dataset) for: {url}")
    if run_status == "FAILED":
        raise PropertyExtractionError(f"Apify actor FAILED for: {url}")
    items = list(client.dataset(dataset_id).iterate_items())
    logger.info("Apify returned %d item(s) for: %s", len(items), url)
    if not items:
        raise PropertyExtractionError(f"Apify returned no data for: {url}")
    return items[0]


async def fetch_property_via_apify(url: str) -> dict:
    return await asyncio.to_thread(_run_apify_sync, url)


class DiscoveredListing(BaseModel):
    """Lightweight candidate from a search-mode Apify call — enough to dedup
    and pre-filter before spending a full detail scrape via fetch_property_via_apify."""
    url: str
    source_listing_id: str
    source_platform: str
    price_aud: Optional[int] = None


def _build_search_input(platform: str, suburb_name: str, filters: dict, max_items: int) -> dict:
    if platform == "realestate":
        return {
            "searchByFilters": {
                "country": "AU",
                "suburb": suburb_name,
                "state": "QLD",
                "channel": "buy",
            },
            "maxItems": max_items,
            "flattenOutput": True,
            "proxy": {"useApifyProxy": True, "apifyProxyGroups": ["RESIDENTIAL"]},
        }
    domain_input: dict = {
        "location": suburb_name,
        "saleType": "buy",
        "limit": max_items,
    }
    if filters.get("price_max") is not None:
        domain_input["priceMax"] = int(filters["price_max"])
    return domain_input


def _run_apify_search_sync(platform: str, suburb_name: str, filters: dict, max_items: int) -> list[dict]:
    client = ApifyClient(settings.APIFY_API_TOKEN)
    actor_id = settings.APIFY_REA_ACTOR_ID if platform == "realestate" else settings.APIFY_DOMAIN_ACTOR_ID
    run_input = _build_search_input(platform, suburb_name, filters, max_items)
    logger.info("Starting Apify search run: actor=%s suburb=%s platform=%s", actor_id, suburb_name, platform)
    run = client.actor(actor_id).call(
        run_input=run_input,
        max_items=max_items,
        max_total_charge_usd=Decimal(str(settings.DISCOVERY_APIFY_MAX_USD_PER_CALL)),
        timeout_secs=600,
    )
    dataset_id = run.get("defaultDatasetId") if run else None
    if not run or not dataset_id:
        logger.warning("Apify search run failed (no dataset): suburb=%s platform=%s", suburb_name, platform)
        return []
    if run.get("status") == "FAILED":
        logger.warning("Apify search actor FAILED: suburb=%s platform=%s", suburb_name, platform)
        return []
    items = list(client.dataset(dataset_id).iterate_items())
    logger.info("Apify search returned %d item(s): suburb=%s platform=%s", len(items), suburb_name, platform)
    return items


async def fetch_new_listings_via_apify(
    platform: str, suburb_name: str, filters: dict, max_items: int
) -> list[DiscoveredListing]:
    """Search-mode call — returns many lightweight listing stubs for a suburb,
    as opposed to fetch_property_via_apify's single-URL detail scrape."""
    raw_items = await asyncio.to_thread(_run_apify_search_sync, platform, suburb_name, filters, max_items)
    listings: list[DiscoveredListing] = []
    for raw in raw_items:
        listing_id = str(raw.get("id") or raw.get("listingId") or raw.get("propertyId") or "")
        url = (
            raw.get("url")
            or raw.get("listingUrl")
            or raw.get("propertyUrl")
            or raw.get("originalSearchUrl")
            or ""
        )
        if not listing_id or not url:
            continue
        listing_price, _, price_high, _ = _extract_price(raw)
        listings.append(DiscoveredListing(
            url=url,
            source_listing_id=listing_id,
            source_platform=platform,
            price_aud=listing_price or price_high,
        ))
    return listings


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
    feats = (
        raw.get("features")
        or raw.get("propertyFeatures")
        or raw.get("listingFeatures")
        or raw.get("outdoorFeatures")
        or raw.get("generalFeatures")
        or raw.get("indoorFeatures")
        or []
    )
    # Some actors return a dict of lists (e.g. {"outdoor": [...], "indoor": [...]})
    if isinstance(feats, dict):
        merged = []
        for v in feats.values():
            if isinstance(v, list):
                merged.extend(v)
        feats = merged
    if not feats or not isinstance(feats, list):
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
