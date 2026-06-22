from datetime import datetime, timezone
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.dependencies import get_current_family
from app.models.family import Family
from app.models.operational import Inspection
from app.models.property import Property
from app.schemas.inspection import InspectionCreate, InspectionResponse, InspectionUpdate

router = APIRouter(prefix="/api/inspections", tags=["inspections"])


async def _load_inspection(inspection_id: UUID, family: Family, db: AsyncSession) -> Inspection:
    result = await db.execute(
        select(Inspection)
        .options(selectinload(Inspection.property))
        .where(
            Inspection.id == inspection_id,
            Inspection.family_id == family.id,
            Inspection.deleted_at.is_(None),
        )
    )
    obj = result.scalar_one_or_none()
    if obj is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Inspection not found")
    return obj


@router.get("", response_model=list[InspectionResponse])
async def list_inspections(
    family: Family = Depends(get_current_family),
    db: AsyncSession = Depends(get_db),
) -> list[InspectionResponse]:
    result = await db.execute(
        select(Inspection)
        .options(selectinload(Inspection.property))
        .where(
            Inspection.family_id == family.id,
            Inspection.deleted_at.is_(None),
        )
        .order_by(Inspection.scheduled_at.asc())
    )
    inspections = result.scalars().all()
    return [InspectionResponse.model_validate(i) for i in inspections]


@router.post("", response_model=InspectionResponse, status_code=status.HTTP_201_CREATED)
async def create_inspection(
    body: InspectionCreate,
    family: Family = Depends(get_current_family),
    db: AsyncSession = Depends(get_db),
) -> InspectionResponse:
    prop_result = await db.execute(
        select(Property).where(
            Property.id == body.property_id,
            Property.family_id == family.id,
            Property.deleted_at.is_(None),
        )
    )
    if prop_result.scalar_one_or_none() is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Property not found")

    inspection = Inspection(
        family_id=family.id,
        property_id=body.property_id,
        scheduled_at=body.scheduled_at,
        notes=body.notes,
        inspection_type=body.inspection_type,
    )
    db.add(inspection)
    await db.commit()

    result = await db.execute(
        select(Inspection)
        .options(selectinload(Inspection.property))
        .where(Inspection.id == inspection.id)
    )
    return InspectionResponse.model_validate(result.scalar_one())


@router.patch("/{inspection_id}", response_model=InspectionResponse)
async def update_inspection(
    inspection_id: UUID,
    body: InspectionUpdate,
    family: Family = Depends(get_current_family),
    db: AsyncSession = Depends(get_db),
) -> InspectionResponse:
    inspection = await _load_inspection(inspection_id, family, db)

    for field, value in body.model_dump(exclude_unset=True).items():
        setattr(inspection, field, value)

    await db.commit()

    result = await db.execute(
        select(Inspection)
        .options(selectinload(Inspection.property))
        .where(Inspection.id == inspection.id)
    )
    return InspectionResponse.model_validate(result.scalar_one())


@router.delete("/{inspection_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_inspection(
    inspection_id: UUID,
    family: Family = Depends(get_current_family),
    db: AsyncSession = Depends(get_db),
) -> None:
    inspection = await _load_inspection(inspection_id, family, db)
    inspection.deleted_at = datetime.now(timezone.utc)
    await db.commit()
