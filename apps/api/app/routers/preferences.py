import uuid as _uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_current_family, get_db
from app.models.family import Family, FamilyPreference
from app.schemas.preference import PreferenceResponse, PreferenceUpdate

router = APIRouter(prefix="/api/preferences", tags=["preferences"])


@router.get("", response_model=list[PreferenceResponse])
async def list_preferences(
    db: AsyncSession = Depends(get_db),
    current_family: Family = Depends(get_current_family),
):
    result = await db.execute(
        select(FamilyPreference)
        .where(
            FamilyPreference.family_id == current_family.id,
            FamilyPreference.status != "Retired",
        )
        .order_by(FamilyPreference.current_weight.desc(), FamilyPreference.attribute.asc())
    )
    return result.scalars().all()


@router.patch("/{preference_id}", response_model=PreferenceResponse)
async def update_preference(
    preference_id: str,
    body: PreferenceUpdate,
    db: AsyncSession = Depends(get_db),
    current_family: Family = Depends(get_current_family),
):
    try:
        pid = _uuid.UUID(preference_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid preference ID")

    result = await db.execute(
        select(FamilyPreference).where(
            FamilyPreference.id == pid,
            FamilyPreference.family_id == current_family.id,
        )
    )
    pref = result.scalar_one_or_none()
    if pref is None:
        raise HTTPException(status_code=404, detail="Preference not found")

    if body.status is not None:
        pref.status = body.status
    if body.current_weight is not None:
        pref.current_weight = body.current_weight
    if body.is_deal_breaker is not None:
        pref.is_deal_breaker = body.is_deal_breaker
    if body.notes is not None:
        pref.notes = body.notes

    await db.commit()
    await db.refresh(pref)
    return pref


@router.delete("/{preference_id}", status_code=204)
async def retire_preference(
    preference_id: str,
    db: AsyncSession = Depends(get_db),
    current_family: Family = Depends(get_current_family),
):
    try:
        pid = _uuid.UUID(preference_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid preference ID")

    result = await db.execute(
        select(FamilyPreference).where(
            FamilyPreference.id == pid,
            FamilyPreference.family_id == current_family.id,
        )
    )
    pref = result.scalar_one_or_none()
    if pref is None:
        raise HTTPException(status_code=404, detail="Preference not found")

    pref.status = "Retired"
    await db.commit()
