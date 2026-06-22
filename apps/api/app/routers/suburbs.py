from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.dependencies import get_db
from app.models.location import School, SchoolCatchment, Suburb, SuburbLifestyleAsset, SuburbMetric
from app.schemas.suburb import (
    SchoolSummaryResponse,
    SuburbDetailResponse,
    SuburbLifestyleResponse,
    SuburbListItem,
    SuburbMetricResponse,
)

router = APIRouter(prefix="/api/suburbs", tags=["suburbs"])


def _name_to_slug(name: str) -> str:
    return name.lower().replace(" ", "-")


@router.get("", response_model=list[SuburbListItem])
async def list_suburbs(db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Suburb)
        .where(Suburb.is_active == True)
        .options(
            selectinload(Suburb.metrics),
            selectinload(Suburb.lifestyle_assets),
        )
        .order_by(Suburb.tier.asc().nulls_last(), Suburb.name.asc())
    )
    suburbs = result.scalars().all()

    items = []
    for s in suburbs:
        community_score = float(s.metrics.community_score) if s.metrics and s.metrics.community_score else None
        lifestyle_score = float(s.lifestyle_assets.lifestyle_score) if s.lifestyle_assets and s.lifestyle_assets.lifestyle_score else None
        beach_minutes = float(s.lifestyle_assets.beach_access_minutes) if s.lifestyle_assets and s.lifestyle_assets.beach_access_minutes else None
        items.append(SuburbListItem(
            id=s.id,
            name=s.name,
            postcode=s.postcode,
            tier=s.tier,
            community_score=community_score,
            lifestyle_score=lifestyle_score,
            beach_access_minutes=beach_minutes,
        ))
    return items


@router.get("/{slug}", response_model=SuburbDetailResponse)
async def get_suburb(slug: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Suburb)
        .where(Suburb.is_active == True)
        .options(
            selectinload(Suburb.metrics),
            selectinload(Suburb.lifestyle_assets),
            selectinload(Suburb.school_catchments).selectinload(SchoolCatchment.school).selectinload(School.metrics),
        )
    )
    suburbs = result.scalars().all()

    suburb = next((s for s in suburbs if _name_to_slug(s.name) == slug), None)
    if suburb is None:
        raise HTTPException(status_code=404, detail="Suburb not found")

    metrics_resp = SuburbMetricResponse.model_validate(suburb.metrics) if suburb.metrics else None
    lifestyle_resp = SuburbLifestyleResponse.model_validate(suburb.lifestyle_assets) if suburb.lifestyle_assets else None

    seen_school_ids = set()
    schools_resp = []
    for catchment in (suburb.school_catchments or []):
        school = catchment.school
        if school and school.id not in seen_school_ids and school.is_active:
            seen_school_ids.add(school.id)
            schools_resp.append(SchoolSummaryResponse(
                id=school.id,
                name=school.name,
                sector=school.sector,
                school_type=school.school_type,
                address_suburb=school.address_suburb,
                year_range=school.year_range,
            ))

    return SuburbDetailResponse(
        id=suburb.id,
        name=suburb.name,
        postcode=suburb.postcode,
        tier=suburb.tier,
        latitude=float(suburb.latitude),
        longitude=float(suburb.longitude),
        lga=suburb.lga,
        metrics=metrics_resp,
        lifestyle=lifestyle_resp,
        schools=schools_resp,
    )
