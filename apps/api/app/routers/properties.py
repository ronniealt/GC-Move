import re
import uuid as _uuid
from datetime import datetime, timezone
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.dependencies import get_current_family
from app.models.family import Family
from app.models.property import Property, PropertyFeature, PropertyImage
from app.schemas.property import (
    PropertyIngestRequest,
    PropertyIngestResponse,
    PropertyListResponse,
    PropertyResponse,
    PropertyUpdateRequest,
)
from app.services import property_ingestion

router = APIRouter(prefix="/api/properties", tags=["properties"])

_REA_PATTERN = re.compile(r"realestate\.com\.au", re.IGNORECASE)
_DOMAIN_PATTERN = re.compile(r"domain\.com\.au", re.IGNORECASE)


def _detect_platform(url: str) -> str:
    if _REA_PATTERN.search(url):
        return "realestate"
    if _DOMAIN_PATTERN.search(url):
        return "domain"
    return ""


@router.post("/ingest", response_model=PropertyIngestResponse, status_code=status.HTTP_202_ACCEPTED)
async def ingest_property(
    body: PropertyIngestRequest,
    background_tasks: BackgroundTasks,
    family: Family = Depends(get_current_family),
    db: AsyncSession = Depends(get_db),
) -> PropertyIngestResponse:
    platform = _detect_platform(body.url)
    if not platform:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="URL must be from realestate.com.au or domain.com.au",
        )

    prop = Property(
        family_id=family.id,
        source_url=body.url,
        source_platform=platform,
        address_street="Pending",
        address_suburb="Pending",
        address_state="QLD",
        address_postcode="0000",
        property_type="house",
        status="ingesting",
    )
    db.add(prop)
    await db.commit()
    await db.refresh(prop)

    background_tasks.add_task(
        property_ingestion.ingest_property,
        str(prop.id),
        body.url,
        str(family.id),
    )

    return PropertyIngestResponse(property_id=prop.id, status="ingesting")


@router.get("", response_model=list[PropertyListResponse])
async def list_properties(
    family: Family = Depends(get_current_family),
    db: AsyncSession = Depends(get_db),
    status_filter: Optional[str] = None,
    discovered_only: bool = False,
) -> list[PropertyListResponse]:
    query = select(Property).where(
        Property.family_id == family.id,
        Property.deleted_at.is_(None),
    )
    if status_filter:
        query = query.where(Property.status == status_filter)
    if discovered_only:
        query = query.where(Property.auto_discovered == True)  # noqa: E712
    query = query.order_by(Property.created_at.desc())

    result = await db.execute(query)
    props = result.scalars().all()
    return [PropertyListResponse.model_validate(p) for p in props]


@router.get("/{property_id}", response_model=PropertyResponse)
async def get_property(
    property_id: str,
    family: Family = Depends(get_current_family),
    db: AsyncSession = Depends(get_db),
) -> PropertyResponse:
    try:
        pid = _uuid.UUID(property_id)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    result = await db.execute(
        select(Property)
        .where(
            Property.id == pid,
            Property.family_id == family.id,
            Property.deleted_at.is_(None),
        )
        .options(
            selectinload(Property.features),
            selectinload(Property.images),
        )
    )
    prop = result.scalar_one_or_none()
    if prop is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    return PropertyResponse.model_validate(prop)


@router.post("/{property_id}/view", response_model=PropertyResponse)
async def mark_property_viewed(
    property_id: str,
    family: Family = Depends(get_current_family),
    db: AsyncSession = Depends(get_db),
) -> PropertyResponse:
    try:
        pid = _uuid.UUID(property_id)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    result = await db.execute(
        select(Property)
        .where(
            Property.id == pid,
            Property.family_id == family.id,
            Property.deleted_at.is_(None),
        )
        .options(
            selectinload(Property.features),
            selectinload(Property.images),
        )
    )
    prop = result.scalar_one_or_none()
    if prop is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    if prop.viewed_at is None:
        prop.viewed_at = datetime.now(timezone.utc)
        await db.commit()
        await db.refresh(prop)

    return PropertyResponse.model_validate(prop)


@router.patch("/{property_id}", response_model=PropertyResponse)
async def update_property(
    property_id: str,
    body: PropertyUpdateRequest,
    family: Family = Depends(get_current_family),
    db: AsyncSession = Depends(get_db),
) -> PropertyResponse:
    try:
        pid = _uuid.UUID(property_id)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    result = await db.execute(
        select(Property)
        .where(
            Property.id == pid,
            Property.family_id == family.id,
            Property.deleted_at.is_(None),
        )
        .options(
            selectinload(Property.features),
            selectinload(Property.images),
        )
    )
    prop = result.scalar_one_or_none()
    if prop is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    for field, value in body.model_dump(exclude_unset=True).items():
        setattr(prop, field, value)

    await db.commit()
    await db.refresh(prop)
    return PropertyResponse.model_validate(prop)
