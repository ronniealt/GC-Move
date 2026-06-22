import asyncio
import logging
from typing import Optional

import httpx
import sentry_sdk

from app.config import settings

logger = logging.getLogger(__name__)

BURLEIGH_LAT = -28.0897
BURLEIGH_LNG = 153.4434

BEACH_ANCHORS = [
    ("Palm Beach", -28.1255, 153.4620),
    ("Currumbin", -28.1479, 153.4778),
    ("Coolangatta", -28.1681, 153.5443),
    ("Broadbeach", -28.0283, 153.4328),
    ("Main Beach", -27.9751, 153.4228),
]

_MAPS_URL = "https://maps.googleapis.com/maps/api/distancematrix/json"


async def calculate_travel_times(
    lat: float,
    lng: float,
    property_id: str,
) -> tuple[Optional[int], Optional[int]]:
    """Return (burleigh_drive_minutes, beach_drive_minutes). Returns (None, None) on any failure."""
    if not settings.GOOGLE_MAPS_API_KEY:
        logger.warning("GOOGLE_MAPS_API_KEY not set — skipping travel time for %s", property_id)
        return None, None

    origins = f"{lat},{lng}"
    destinations = [
        f"{BURLEIGH_LAT},{BURLEIGH_LNG}",
        *[f"{blat},{blng}" for _, blat, blng in BEACH_ANCHORS],
    ]

    try:
        data = await asyncio.wait_for(
            _call_distance_matrix(origins, destinations),
            timeout=15.0,
        )
        elements = (data.get("rows") or [{}])[0].get("elements", [])
        if not elements:
            return None, None

        burleigh_mins = _extract_minutes(elements[0])

        beach_candidates = [
            _extract_minutes(elements[i])
            for i in range(1, len(elements))
            if i < len(elements)
        ]
        beach_mins = min((m for m in beach_candidates if m is not None), default=None)

        return burleigh_mins, beach_mins

    except Exception as e:
        sentry_sdk.capture_exception(e)
        logger.warning("Travel time calculation failed for %s: %s", property_id, e)
        return None, None


async def _call_distance_matrix(origins: str, destinations: list[str]) -> dict:
    async with httpx.AsyncClient(timeout=12.0) as client:
        resp = await client.get(
            _MAPS_URL,
            params={
                "origins": origins,
                "destinations": "|".join(destinations),
                "mode": "driving",
                "key": settings.GOOGLE_MAPS_API_KEY,
            },
        )
        resp.raise_for_status()
        return resp.json()


def _extract_minutes(element: dict) -> Optional[int]:
    if not element or element.get("status") != "OK":
        return None
    value_secs = (element.get("duration") or {}).get("value")
    if value_secs is None:
        return None
    return round(value_secs / 60)
