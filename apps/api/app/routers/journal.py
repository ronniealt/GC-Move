import uuid as _uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_current_family, get_db
from app.models.family import Family
from app.models.intelligence import DecisionJournalEntry
from app.models.property import Property
from app.schemas.journal import JournalEntryCreate, JournalEntryResponse, JournalPropertySnippet

router = APIRouter(prefix="/api/journal", tags=["journal"])


async def _load_property_snippet(db: AsyncSession, property_id, family_id) -> JournalPropertySnippet | None:
    if property_id is None:
        return None
    result = await db.execute(
        select(Property).where(
            Property.id == property_id,
            Property.family_id == family_id,
            Property.deleted_at.is_(None),
        )
    )
    prop = result.scalar_one_or_none()
    if prop is None:
        return None
    return JournalPropertySnippet(
        id=prop.id,
        address_street=prop.address_street,
        address_suburb=prop.address_suburb,
        listing_price_aud=prop.listing_price_aud,
    )


def _entry_to_response(entry: DecisionJournalEntry, property_snippet: JournalPropertySnippet | None) -> JournalEntryResponse:
    return JournalEntryResponse(
        id=entry.id,
        family_id=entry.family_id,
        property_id=entry.property_id,
        suburb_id=entry.suburb_id,
        entry_type=entry.entry_type,
        title=entry.title,
        body=entry.body,
        mood=entry.mood,
        tags=entry.tags,
        is_pinned=entry.is_pinned,
        created_at=entry.created_at,
        updated_at=entry.updated_at,
        property=property_snippet,
    )


@router.get("", response_model=list[JournalEntryResponse])
async def list_journal_entries(
    db: AsyncSession = Depends(get_db),
    current_family: Family = Depends(get_current_family),
):
    result = await db.execute(
        select(DecisionJournalEntry)
        .where(
            DecisionJournalEntry.family_id == current_family.id,
            DecisionJournalEntry.deleted_at.is_(None),
        )
        .order_by(DecisionJournalEntry.is_pinned.desc(), DecisionJournalEntry.created_at.desc())
    )
    entries = result.scalars().all()

    responses = []
    for entry in entries:
        snippet = await _load_property_snippet(db, entry.property_id, current_family.id)
        responses.append(_entry_to_response(entry, snippet))
    return responses


@router.post("", response_model=JournalEntryResponse, status_code=201)
async def create_journal_entry(
    body: JournalEntryCreate,
    db: AsyncSession = Depends(get_db),
    current_family: Family = Depends(get_current_family),
):
    entry = DecisionJournalEntry(
        family_id=current_family.id,
        property_id=body.property_id,
        suburb_id=body.suburb_id,
        entry_type=body.entry_type,
        title=body.title,
        body=body.body,
        mood=body.mood,
        tags=body.tags,
        is_pinned=body.is_pinned,
    )
    db.add(entry)
    await db.commit()
    await db.refresh(entry)

    snippet = await _load_property_snippet(db, entry.property_id, current_family.id)
    return _entry_to_response(entry, snippet)


@router.get("/{entry_id}", response_model=JournalEntryResponse)
async def get_journal_entry(
    entry_id: str,
    db: AsyncSession = Depends(get_db),
    current_family: Family = Depends(get_current_family),
):
    try:
        eid = _uuid.UUID(entry_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid entry ID")

    result = await db.execute(
        select(DecisionJournalEntry).where(
            DecisionJournalEntry.id == eid,
            DecisionJournalEntry.family_id == current_family.id,
            DecisionJournalEntry.deleted_at.is_(None),
        )
    )
    entry = result.scalar_one_or_none()
    if entry is None:
        raise HTTPException(status_code=404, detail="Journal entry not found")

    snippet = await _load_property_snippet(db, entry.property_id, current_family.id)
    return _entry_to_response(entry, snippet)


@router.delete("/{entry_id}", status_code=204)
async def delete_journal_entry(
    entry_id: str,
    db: AsyncSession = Depends(get_db),
    current_family: Family = Depends(get_current_family),
):
    try:
        eid = _uuid.UUID(entry_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid entry ID")

    result = await db.execute(
        select(DecisionJournalEntry).where(
            DecisionJournalEntry.id == eid,
            DecisionJournalEntry.family_id == current_family.id,
            DecisionJournalEntry.deleted_at.is_(None),
        )
    )
    entry = result.scalar_one_or_none()
    if entry is None:
        raise HTTPException(status_code=404, detail="Journal entry not found")

    entry.deleted_at = func.now()
    await db.commit()
