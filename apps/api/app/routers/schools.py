from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.dependencies import get_db
from app.models.location import School, SchoolMetric
from app.schemas.school import SchoolListItem, SchoolMetricResponse

router = APIRouter(prefix="/api/schools", tags=["schools"])


@router.get("", response_model=list[SchoolListItem])
async def list_schools(db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(School)
        .where(School.is_active == True)
        .options(selectinload(School.metrics))
        .order_by(School.name.asc())
    )
    schools = result.scalars().all()

    items = []
    for s in schools:
        metrics_resp = SchoolMetricResponse.model_validate(s.metrics) if s.metrics else None
        items.append(SchoolListItem(
            id=s.id,
            name=s.name,
            school_type=s.school_type,
            sector=s.sector,
            address_suburb=s.address_suburb,
            address_postcode=s.address_postcode,
            year_range=s.year_range,
            icsea=s.icsea,
            total_enrolments=s.total_enrolments,
            website_url=s.website_url,
            metrics=metrics_resp,
        ))
    return items
