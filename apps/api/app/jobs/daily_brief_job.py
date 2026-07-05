"""Daily Brief job — emails each family their top new property recommendations
for families that have opted into the daily digest.

Runnable identically by Railway Cron and a developer:

    python -m app.jobs.daily_brief_job
    python -m app.jobs.daily_brief_job --family-id=<uuid> --dry-run
    python -m app.jobs.daily_brief_job --family-id=<uuid> --force
"""
import argparse
import asyncio
import logging
import uuid as _uuid
from datetime import datetime, timedelta, timezone

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.database import AsyncSessionLocal
from app.models.family import Family
from app.models.intelligence import Recommendation
from app.models.operational import NotificationSettings
from app.models.property import Property
from app.services.email import send_email

logger = logging.getLogger(__name__)

BRISBANE_UTC_OFFSET = timedelta(hours=10)  # Queensland does not observe daylight saving.


def _brisbane_now() -> datetime:
    return datetime.now(timezone.utc) + BRISBANE_UTC_OFFSET


async def run_daily_brief(
    family_id: str | None = None,
    dry_run: bool = False,
    force: bool = False,
) -> dict:
    """Returns a small summary dict for logging/testing — not used by Railway Cron directly."""
    summary = {"families_checked": 0, "emails_sent": 0, "skipped_no_new": 0}

    brisbane_now = _brisbane_now()

    async with AsyncSessionLocal() as db:
        query = (
            select(Family)
            .join(NotificationSettings, NotificationSettings.family_id == Family.id)
            .where(
                Family.is_active.is_(True),
                Family.onboarding_completed.is_(True),
                NotificationSettings.email_daily_digest.is_(True),
            )
            .options(selectinload(Family.users))
        )
        if family_id:
            query = query.where(Family.id == _uuid.UUID(family_id))
        families = (await db.execute(query)).scalars().all()

        for family in families:
            summary["families_checked"] += 1

            settings_result = await db.execute(
                select(NotificationSettings).where(NotificationSettings.family_id == family.id)
            )
            notification_settings = settings_result.scalar_one_or_none()
            if notification_settings is None:
                # Shouldn't happen given the join above, but guard defensively.
                continue

            if not force:
                if notification_settings.digest_time is None:
                    continue
                if brisbane_now.hour != notification_settings.digest_time.hour:
                    continue

                if notification_settings.last_digest_sent_at is not None:
                    last_sent_brisbane = notification_settings.last_digest_sent_at + BRISBANE_UTC_OFFSET
                    if last_sent_brisbane.date() == brisbane_now.date():
                        continue

            since = notification_settings.last_digest_sent_at or (
                datetime.now(timezone.utc) - timedelta(days=1)
            )

            recs_result = await db.execute(
                select(Recommendation)
                .join(Property, Recommendation.property_id == Property.id)
                .where(
                    Recommendation.family_id == family.id,
                    Property.status == "evaluated",
                    Property.deleted_at.is_(None),
                    Property.created_at > since,
                )
                .order_by(Recommendation.family_fit_score.desc())
                .limit(3)
            )
            recs = recs_result.scalars().all()

            if not recs:
                summary["skipped_no_new"] += 1
                logger.info("No new recommendations for family=%s, skipping digest", family.id)
                continue

            property_ids = [r.property_id for r in recs]
            props_result = await db.execute(
                select(Property).where(Property.id.in_(property_ids))
            )
            props_by_id = {str(p.id): p for p in props_result.scalars().all()}

            if dry_run:
                headlines = []
                for r in recs:
                    prop = props_by_id.get(str(r.property_id))
                    address = prop.address_street if prop else "Unknown"
                    headlines.append(f"{address} ({r.headline or 'no headline'})")
                logger.info(
                    "[dry-run] family=%s would send digest with %d recommendation(s): %s",
                    family.id, len(recs), headlines,
                )
                continue

            html = _build_digest_html(family.display_name, recs, props_by_id)
            subject = f"Your Daily Brief — {len(recs)} new recommendation(s) for {family.display_name}"

            recipient = next((u.email for u in family.users if u.role == "primary"), None)
            if recipient is None and family.users:
                recipient = family.users[0].email
            if recipient is None:
                logger.warning("Family %s has no users to email digest to, skipping", family.id)
                continue

            sent = await send_email(recipient, subject, html)
            if sent:
                notification_settings.last_digest_sent_at = datetime.now(timezone.utc)
                await db.commit()
                summary["emails_sent"] += 1
            else:
                logger.error("Failed to send daily brief to family=%s", family.id)

    logger.info("Daily brief run complete: %s", summary)
    return summary


def _build_digest_html(family_name: str, recs: list[Recommendation], props_by_id: dict) -> str:
    rows = []
    for rec in recs:
        prop = props_by_id.get(str(rec.property_id))
        address = prop.address_street if prop else "Unknown address"
        suburb = prop.address_suburb if prop else ""
        headline = rec.headline or ""
        summary_text = rec.summary or ""
        score = rec.family_fit_score if rec.family_fit_score is not None else "N/A"
        rows.append(
            "<li>"
            f"<strong>{address}, {suburb}</strong> — Family Fit Score: {score}<br>"
            f"{headline}<br>"
            f"<span>{summary_text}</span>"
            "</li>"
        )
    return (
        f"<p>Good morning, {family_name}!</p>"
        "<p>Here are your top new property recommendations:</p>"
        f"<ul>{''.join(rows)}</ul>"
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Send the daily brief digest email to opted-in families")
    parser.add_argument("--family-id", default=None, help="Scope to a single family (for local testing)")
    parser.add_argument("--dry-run", action="store_true", help="Log what would be sent without sending/updating")
    parser.add_argument("--force", action="store_true", help="Bypass the hourly digest_time gate (manual testing)")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO)
    asyncio.run(run_daily_brief(family_id=args.family_id, dry_run=args.dry_run, force=args.force))


if __name__ == "__main__":
    main()
