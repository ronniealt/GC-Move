"""Auto-discovery job — polls realestate.com.au/domain.com.au for new listings
matching each family's target suburbs + budget, and hands new ones to the
existing single-URL ingestion/scoring pipeline. No scoring logic lives here.

Runnable identically by Railway Cron and a developer:

    python -m app.jobs.discovery_job
    python -m app.jobs.discovery_job --family-id=<uuid> --dry-run
"""
import argparse
import asyncio
import logging
import uuid as _uuid

import sentry_sdk
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.config import settings
from app.database import AsyncSessionLocal
from app.models.family import Family, FamilySuburb
from app.models.property import Property, PropertyHistory
from app.services.apify_scraper import fetch_new_listings_via_apify
from app.services.property_ingestion import ingest_property

logger = logging.getLogger(__name__)

PLATFORMS = ("realestate", "domain")


async def run_discovery(family_id: str | None = None, dry_run: bool = False) -> dict:
    """Returns a small summary dict for logging/testing — not used by Railway Cron directly."""
    summary = {"families_scanned": 0, "candidates_found": 0, "new_ingested": 0, "errors": 0}

    async with AsyncSessionLocal() as db:
        query = select(Family).where(Family.is_active.is_(True), Family.onboarding_completed.is_(True))
        if family_id:
            query = query.where(Family.id == _uuid.UUID(family_id))
        query = query.options(
            selectinload(Family.target_suburbs).selectinload(FamilySuburb.suburb),
            selectinload(Family.non_negotiables),
        )
        families = (await db.execute(query)).scalars().all()

    semaphore = asyncio.Semaphore(3)

    for family in families:
        summary["families_scanned"] += 1
        target_suburbs = [ts for ts in family.target_suburbs if ts.deleted_at is None]
        if not target_suburbs:
            continue

        new_ingested_this_family = 0
        apify_spend_this_family = 0.0

        for target in target_suburbs:
            if new_ingested_this_family >= settings.DISCOVERY_MAX_NEW_PER_FAMILY_RUN:
                break
            if apify_spend_this_family >= settings.DISCOVERY_APIFY_MAX_USD_PER_RUN:
                logger.warning("Family %s hit per-run Apify spend cap, stopping early", family.id)
                break

            for platform in PLATFORMS:
                try:
                    candidates = await fetch_new_listings_via_apify(
                        platform=platform,
                        suburb_name=target.suburb.name,
                        filters={"price_max": family.budget_max_aud},
                        max_items=settings.DISCOVERY_SEARCH_MAX_ITEMS,
                    )
                    apify_spend_this_family += settings.DISCOVERY_APIFY_MAX_USD_PER_CALL
                    summary["candidates_found"] += len(candidates)

                    # Pre-filter by budget before spending anything else on this candidate.
                    if family.budget_max_aud:
                        candidates = [
                            c for c in candidates
                            if c.price_aud is None or c.price_aud <= family.budget_max_aud
                        ]

                    # Dedup against this family's existing Property rows — the primary
                    # cost-avoidance layer; the DB unique index is the hard backstop.
                    listing_ids = [c.source_listing_id for c in candidates]
                    if listing_ids:
                        async with AsyncSessionLocal() as dedup_db:
                            existing_result = await dedup_db.execute(
                                select(Property.source_listing_id).where(
                                    Property.family_id == family.id,
                                    Property.source_platform == platform,
                                    Property.source_listing_id.in_(listing_ids),
                                    Property.deleted_at.is_(None),
                                )
                            )
                            known_ids = {row[0] for row in existing_result.all()}
                        candidates = [c for c in candidates if c.source_listing_id not in known_ids]

                    if dry_run:
                        logger.info(
                            "[dry-run] family=%s suburb=%s platform=%s new_candidates=%d",
                            family.id, target.suburb.name, platform, len(candidates),
                        )
                        continue

                    async def _ingest_one(candidate):
                        nonlocal new_ingested_this_family
                        async with semaphore:
                            async with AsyncSessionLocal() as ingest_db:
                                prop = Property(
                                    family_id=family.id,
                                    source_url=candidate.url,
                                    source_platform=platform,
                                    source_listing_id=candidate.source_listing_id,
                                    address_street="Pending",
                                    address_suburb=target.suburb.name,
                                    address_state="QLD",
                                    address_postcode=target.suburb.postcode,
                                    property_type="house",
                                    status="ingesting",
                                    auto_discovered=True,
                                )
                                ingest_db.add(prop)
                                try:
                                    await ingest_db.commit()
                                except Exception:
                                    # Race: another concurrent run/candidate already claimed this
                                    # listing between our dedup check and this insert.
                                    await ingest_db.rollback()
                                    return
                                await ingest_db.refresh(prop)
                                ingest_db.add(PropertyHistory(
                                    family_id=family.id,
                                    property_id=prop.id,
                                    event_type="listed",
                                    new_value=candidate.url,
                                    notes=f"Auto-discovered in {target.suburb.name} ({platform})",
                                    source="discovery",
                                ))
                                await ingest_db.commit()
                            await ingest_property(str(prop.id), candidate.url, str(family.id))
                            new_ingested_this_family += 1
                            summary["new_ingested"] += 1

                    remaining_budget = settings.DISCOVERY_MAX_NEW_PER_FAMILY_RUN - new_ingested_this_family
                    await asyncio.gather(*[_ingest_one(c) for c in candidates[:remaining_budget]])

                except Exception as e:
                    summary["errors"] += 1
                    sentry_sdk.capture_exception(e)
                    logger.error(
                        "Discovery failed for family=%s suburb=%s platform=%s: %s",
                        family.id, target.suburb.name, platform, e,
                    )

        logger.info(
            "Family %s discovery done: new_ingested=%d est_apify_spend_usd=%.2f",
            family.id, new_ingested_this_family, apify_spend_this_family,
        )

    if summary["errors"] > 0:
        logger.warning("Discovery run had %d suburb/platform failures — check Sentry for details", summary["errors"])
    logger.info("Discovery run complete: %s", summary)
    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description="Poll REA/Domain for new listings matching family criteria")
    parser.add_argument("--family-id", default=None, help="Scope to a single family (for local testing)")
    parser.add_argument("--dry-run", action="store_true", help="Search and log candidates without writing/ingesting")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO)
    asyncio.run(run_discovery(family_id=args.family_id, dry_run=args.dry_run))


if __name__ == "__main__":
    main()
