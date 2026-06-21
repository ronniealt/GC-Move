from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_current_family
from app.models.family import Family
from app.models.property import Property
from app.schemas.dashboard import DashboardResponse

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])


@router.get("", response_model=DashboardResponse)
async def get_dashboard(
    family: Family = Depends(get_current_family),
    db: AsyncSession = Depends(get_db),
) -> DashboardResponse:
    total_result = await db.execute(
        select(func.count(Property.id)).where(
            Property.family_id == family.id,
            Property.deleted_at.is_(None),
        )
    )
    properties_reviewed = total_result.scalar_one() or 0

    return DashboardResponse(
        top_recommendations=[],
        properties_reviewed=properties_reviewed,
        new_this_week=0,
        shortlist_count=0,
        recent_journal_count=0,
    )
