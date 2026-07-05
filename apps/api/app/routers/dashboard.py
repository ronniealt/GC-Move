from datetime import datetime, timedelta, timezone
from typing import Optional

from fastapi import APIRouter, Depends
from sqlalchemy import case, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.dependencies import get_current_family
from app.models.family import Family
from app.models.intelligence import (
    DecisionJournalEntry,
    EvaluationScore,
    PropertyEvaluation,
    Recommendation,
)
from app.models.operational import Inspection
from app.models.property import Property
from app.schemas.dashboard import DashboardResponse, TopPropertyItem, UpcomingInspectionItem
from app.schemas.evaluation import EvaluationScoresResponse

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])


def _f(val) -> Optional[float]:
    return float(val) if val is not None else None


@router.get("", response_model=DashboardResponse)
async def get_dashboard(
    family: Family = Depends(get_current_family),
    db: AsyncSession = Depends(get_db),
) -> DashboardResponse:
    one_week_ago = datetime.now(timezone.utc) - timedelta(days=7)

    # Merge all 3 property counts into a single query
    counts_result = await db.execute(
        select(
            func.count(Property.id).label("total"),
            func.count(case((Property.created_at >= one_week_ago, Property.id))).label("new_this_week"),
            func.count(case((Property.status == "shortlisted", Property.id))).label("shortlist"),
        ).where(
            Property.family_id == family.id,
            Property.deleted_at.is_(None),
        )
    )
    counts_row = counts_result.one()
    properties_reviewed = counts_row.total or 0
    new_this_week = counts_row.new_this_week or 0
    shortlist_count = counts_row.shortlist or 0

    # Recent journal entries (last 7 days)
    journal_result = await db.execute(
        select(func.count(DecisionJournalEntry.id)).where(
            DecisionJournalEntry.family_id == family.id,
            DecisionJournalEntry.deleted_at.is_(None),
            DecisionJournalEntry.created_at >= one_week_ago,
        )
    )
    recent_journal_count = journal_result.scalar_one() or 0

    # Top recommendations
    recs_result = await db.execute(
        select(Recommendation)
        .options(
            selectinload(Recommendation.evaluation).selectinload(PropertyEvaluation.scores),
        )
        .join(Property, Recommendation.property_id == Property.id)
        .where(
            Recommendation.family_id == family.id,
            Recommendation.status == "active",
            Property.deleted_at.is_(None),
        )
        .order_by(Recommendation.family_fit_score.desc())
        .limit(3)
    )
    recs = recs_result.scalars().all()

    top_recs: list[TopPropertyItem] = []
    if recs:
        property_ids = [r.property_id for r in recs]
        props_result = await db.execute(
            select(Property)
            .options(
                selectinload(Property.images),
                selectinload(Property.suburb),
            )
            .where(Property.id.in_(property_ids))
        )
        props_by_id = {str(p.id): p for p in props_result.scalars().all()}

        for rec in recs:
            prop = props_by_id.get(str(rec.property_id))
            if not prop:
                continue

            evaluation = rec.evaluation
            scores_obj = evaluation.scores if evaluation else None

            hero_image = prop.images[0].image_url if prop.images else None

            scores_response = None
            if scores_obj:
                scores_response = EvaluationScoresResponse(
                    community_score=_f(scores_obj.community_score),
                    lifestyle_score=_f(scores_obj.lifestyle_score),
                    school_score=_f(scores_obj.school_score),
                    property_score=_f(scores_obj.property_score),
                    financial_score=_f(scores_obj.financial_score),
                    risk_score=_f(scores_obj.risk_score),
                    family_fit_score=_f(scores_obj.family_fit_score),
                    five_year_fit_score=_f(scores_obj.five_year_fit_score),
                )

            top_recs.append(TopPropertyItem(
                id=prop.id,
                address_street=prop.address_street,
                address_suburb=prop.address_suburb,
                listing_price_aud=prop.listing_price_aud,
                bedrooms=prop.bedrooms,
                bathrooms=_f(prop.bathrooms),
                status=prop.status,
                rank_position=rec.rank_position,
                family_fit_score=_f(rec.family_fit_score),
                confidence_score=_f(evaluation.confidence_score) if evaluation else None,
                executive_summary=evaluation.executive_summary if evaluation else None,
                suburb_tier=prop.suburb.tier if prop.suburb else None,
                scores=scores_response,
                hero_image_url=hero_image,
                auto_discovered=prop.auto_discovered,
                viewed_at=prop.viewed_at,
            ))

    # Upcoming inspections (next 2 scheduled)
    upcoming_result = await db.execute(
        select(Inspection)
        .options(selectinload(Inspection.property))
        .where(
            Inspection.family_id == family.id,
            Inspection.deleted_at.is_(None),
            Inspection.status == "scheduled",
        )
        .order_by(Inspection.scheduled_at.asc())
        .limit(2)
    )
    upcoming_inspections = [
        UpcomingInspectionItem(
            id=i.id,
            property_id=i.property_id,
            property_address=i.property.address_street if i.property else "Unknown",
            property_suburb=i.property.address_suburb if i.property else "",
            scheduled_at=i.scheduled_at,
            status=i.status,
        )
        for i in upcoming_result.scalars().all()
    ]

    return DashboardResponse(
        family_display_name=family.display_name,
        top_recommendations=top_recs,
        properties_reviewed=properties_reviewed,
        new_this_week=new_this_week,
        shortlist_count=shortlist_count,
        recent_journal_count=recent_journal_count,
        upcoming_inspections=upcoming_inspections,
    )
