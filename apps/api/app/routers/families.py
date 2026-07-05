import logging
import secrets
from datetime import datetime, timedelta, timezone
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

logger = logging.getLogger(__name__)
from pydantic import BaseModel, EmailStr
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_current_family, get_current_family_user, verify_clerk_jwt
from app.models.family import Family, FamilyInvite, FamilyMember, FamilyNonNegotiable, FamilySuburb, FamilyUser
from app.models.operational import NotificationSettings
from app.services.email import send_email
from app.schemas.family import (
    FamilyMemberCreate,
    FamilyMemberResponse,
    FamilyNonNegotiableResponse,
    FamilyResponse,
    FamilySuburbsResponse,
    FamilyUpdate,
    InviteCreateRequest,
    NonNegotiablesSetRequest,
    NotificationSettingsResponse,
    NotificationSettingsUpdate,
    SuburbTargetsSetRequest,
)

# Onboarding checkbox label -> (criterion_key, comparator, value). "Under $2M"/
# "Under $1.5M" are handled separately as a direct budget_max_aud ceiling since
# they'd otherwise duplicate the budget field as a redundant criterion row.
NON_NEGOTIABLE_LABEL_MAP: dict[str, tuple[str, str, str]] = {
    "4+ bedrooms": ("min_bedrooms", "gte", "4"),
    "Pool": ("has_pool", "has", "true"),
    "Double garage": ("has_double_garage", "has", "true"),
    "Somerset College catchment": ("school_catchment", "eq", "Somerset College"),
    "Beach < 10 min": ("max_beach_drive_minutes", "lte", "10"),
    "Home office": ("has_home_office", "has", "true"),
}

BUDGET_LABEL_CEILING_AUD: dict[str, int] = {
    "Under $2M": 2_000_000,
    "Under $1.5M": 1_500_000,
}

MAX_TARGET_SUBURBS = 7

VALID_PROPERTY_TYPES = {"house", "townhouse", "unit", "acreage"}

router = APIRouter(prefix="/api/families", tags=["families"])


class FamilyCreateBody(BaseModel):
    display_name: str
    user_display_name: str
    user_email: EmailStr
    primary_suburb_target: Optional[str] = None
    budget_min_aud: Optional[int] = None
    budget_max_aud: Optional[int] = None


async def _send_invite_email(
    to_email: str,
    family_name: str,
    inviter_name: str,
    token: str,
) -> None:
    invite_url = f"http://localhost:3000/invite/accept?token={token}"
    subject = f"Join {family_name} on GC Move OS"
    html = (
        f"<p>{inviter_name} has invited you to join their family on GC Move OS.</p>"
        f"<p><a href='{invite_url}'>Accept invitation</a></p>"
        "<p>This link expires in 7 days.</p>"
    )
    await send_email(to_email, subject, html)


@router.post("", response_model=FamilyResponse, status_code=status.HTTP_201_CREATED)
async def create_family(
    body: FamilyCreateBody,
    clerk_user_id: str = Depends(verify_clerk_jwt),
    db: AsyncSession = Depends(get_db),
) -> FamilyResponse:
    """Create a new family and link the authenticated user as primary."""
    existing = await db.execute(
        select(FamilyUser).where(FamilyUser.clerk_user_id == clerk_user_id)
    )
    if existing.scalar_one_or_none() is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User already belongs to a family.",
        )

    family = Family(
        display_name=body.display_name,
        primary_suburb_target=body.primary_suburb_target,
        budget_min_aud=body.budget_min_aud,
        budget_max_aud=body.budget_max_aud,
    )
    db.add(family)
    await db.flush()

    family_user = FamilyUser(
        family_id=family.id,
        clerk_user_id=clerk_user_id,
        role="primary",
        display_name=body.user_display_name,
        email=str(body.user_email),
    )
    db.add(family_user)
    db.add(NotificationSettings(family_id=family.id))
    await db.commit()
    await db.refresh(family)
    return FamilyResponse.model_validate(family)


@router.get("/me", response_model=FamilyResponse)
async def get_my_family(
    family: Family = Depends(get_current_family),
) -> FamilyResponse:
    return FamilyResponse.model_validate(family)


@router.patch("/{family_id}", response_model=FamilyResponse)
async def update_family(
    family_id: str,
    body: FamilyUpdate,
    family: Family = Depends(get_current_family),
    db: AsyncSession = Depends(get_db),
) -> FamilyResponse:
    if str(family.id) != family_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)

    for field, value in body.model_dump(exclude_unset=True).items():
        setattr(family, field, value)

    await db.commit()
    await db.refresh(family)
    return FamilyResponse.model_validate(family)


@router.post("/{family_id}/members", response_model=FamilyMemberResponse, status_code=status.HTTP_201_CREATED)
async def add_member(
    family_id: str,
    body: FamilyMemberCreate,
    family: Family = Depends(get_current_family),
    db: AsyncSession = Depends(get_db),
) -> FamilyMemberResponse:
    if str(family.id) != family_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)

    member = FamilyMember(
        family_id=family.id,
        first_name=body.first_name,
        role=body.role,
        age=body.age,
        birth_year=body.birth_year,
        notes=body.notes,
        avatar_emoji=body.avatar_emoji or "👤",
    )
    db.add(member)
    await db.commit()
    await db.refresh(member)
    return FamilyMemberResponse.model_validate(member)


@router.get("/{family_id}/members", response_model=list[FamilyMemberResponse])
async def list_members(
    family_id: str,
    family: Family = Depends(get_current_family),
    db: AsyncSession = Depends(get_db),
) -> list[FamilyMemberResponse]:
    if str(family.id) != family_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)

    result = await db.execute(
        select(FamilyMember).where(
            FamilyMember.family_id == family.id,
            FamilyMember.deleted_at.is_(None),
        )
    )
    members = result.scalars().all()
    return [FamilyMemberResponse.model_validate(m) for m in members]


@router.post("/{family_id}/invite", status_code=status.HTTP_201_CREATED)
async def send_invite(
    family_id: str,
    body: InviteCreateRequest,
    family: Family = Depends(get_current_family),
    family_user: FamilyUser = Depends(get_current_family_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    if str(family.id) != family_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)

    if family_user.role != "primary":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the primary user can send invites.",
        )

    existing_invite = await db.execute(
        select(FamilyInvite).where(
            FamilyInvite.family_id == family.id,
            FamilyInvite.email == str(body.email),
            FamilyInvite.status == "pending",
        )
    )
    if existing_invite.scalar_one_or_none() is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A pending invite already exists for this email.",
        )

    token = secrets.token_urlsafe(32)
    invite = FamilyInvite(
        family_id=family.id,
        invited_by_user_id=family_user.id,
        email=str(body.email),
        role=body.role,
        invite_token=token,
        expires_at=datetime.now(timezone.utc) + timedelta(days=7),
    )
    db.add(invite)
    await db.commit()

    await _send_invite_email(
        to_email=str(body.email),
        family_name=family.display_name,
        inviter_name=family_user.display_name,
        token=token,
    )

    return {"message": "Invite sent", "token": token}


@router.delete("/{family_id}/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_family_user(
    family_id: str,
    user_id: str,
    family: Family = Depends(get_current_family),
    family_user: FamilyUser = Depends(get_current_family_user),
    db: AsyncSession = Depends(get_db),
) -> None:
    if str(family.id) != family_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)

    if family_user.role != "primary":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the primary user can remove family members.",
        )

    result = await db.execute(
        select(FamilyUser).where(
            FamilyUser.id == UUID(user_id),
            FamilyUser.family_id == family.id,
            FamilyUser.deleted_at.is_(None),
        )
    )
    target_user = result.scalar_one_or_none()
    if target_user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    if target_user.role == "primary":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot remove the primary user.",
        )

    target_user.deleted_at = datetime.now(timezone.utc)
    await db.commit()


@router.put("/{family_id}/non-negotiables", status_code=status.HTTP_200_OK)
async def set_non_negotiables(
    family_id: str,
    body: NonNegotiablesSetRequest,
    family: Family = Depends(get_current_family),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Replace the family's full non-negotiables set from onboarding/settings checkbox labels."""
    if str(family.id) != family_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)

    existing = await db.execute(
        select(FamilyNonNegotiable).where(
            FamilyNonNegotiable.family_id == family.id,
            FamilyNonNegotiable.deleted_at.is_(None),
        )
    )
    now = datetime.now(timezone.utc)
    for row in existing.scalars().all():
        row.deleted_at = now

    tightest_ceiling: Optional[int] = None
    for label in body.labels:
        if label in BUDGET_LABEL_CEILING_AUD:
            ceiling = BUDGET_LABEL_CEILING_AUD[label]
            tightest_ceiling = ceiling if tightest_ceiling is None else min(tightest_ceiling, ceiling)
            continue
        mapped = NON_NEGOTIABLE_LABEL_MAP.get(label)
        if mapped is None:
            continue
        criterion_key, comparator, value = mapped
        db.add(FamilyNonNegotiable(
            family_id=family.id,
            criterion_key=criterion_key,
            comparator=comparator,
            value=value,
            label=label,
            source="onboarding",
        ))

    if tightest_ceiling is not None:
        if family.budget_max_aud is None or tightest_ceiling < family.budget_max_aud:
            family.budget_max_aud = tightest_ceiling

    if body.property_type and body.property_type in VALID_PROPERTY_TYPES:
        db.add(FamilyNonNegotiable(
            family_id=family.id,
            criterion_key="property_type",
            comparator="eq",
            value=body.property_type,
            label=f"Property type: {body.property_type.title()}",
            source="onboarding",
        ))

    await db.commit()
    return {"message": "Non-negotiables updated"}


@router.get("/{family_id}/non-negotiables", response_model=list[FamilyNonNegotiableResponse])
async def list_non_negotiables(
    family_id: str,
    family: Family = Depends(get_current_family),
    db: AsyncSession = Depends(get_db),
) -> list[FamilyNonNegotiableResponse]:
    if str(family.id) != family_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)

    result = await db.execute(
        select(FamilyNonNegotiable).where(
            FamilyNonNegotiable.family_id == family.id,
            FamilyNonNegotiable.deleted_at.is_(None),
        )
    )
    return [FamilyNonNegotiableResponse.model_validate(r) for r in result.scalars().all()]


@router.put("/{family_id}/suburbs", status_code=status.HTTP_200_OK)
async def set_target_suburbs(
    family_id: str,
    body: SuburbTargetsSetRequest,
    family: Family = Depends(get_current_family),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Replace the family's full target-suburb list, capped to keep discovery/scoring cost bounded."""
    if str(family.id) != family_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
    if len(body.suburb_ids) > MAX_TARGET_SUBURBS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Maximum {MAX_TARGET_SUBURBS} target suburbs",
        )

    existing = await db.execute(
        select(FamilySuburb).where(
            FamilySuburb.family_id == family.id,
            FamilySuburb.deleted_at.is_(None),
        )
    )
    now = datetime.now(timezone.utc)
    for row in existing.scalars().all():
        row.deleted_at = now

    for suburb_id in body.suburb_ids:
        db.add(FamilySuburb(family_id=family.id, suburb_id=suburb_id))

    await db.commit()
    return {"message": "Target suburbs updated"}


@router.get("/{family_id}/suburbs", response_model=FamilySuburbsResponse)
async def list_target_suburbs(
    family_id: str,
    family: Family = Depends(get_current_family),
    db: AsyncSession = Depends(get_db),
) -> FamilySuburbsResponse:
    if str(family.id) != family_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)

    result = await db.execute(
        select(FamilySuburb).where(
            FamilySuburb.family_id == family.id,
            FamilySuburb.deleted_at.is_(None),
        )
    )
    return FamilySuburbsResponse(suburb_ids=[r.suburb_id for r in result.scalars().all()])


@router.get("/{family_id}/notification-settings", response_model=NotificationSettingsResponse)
async def get_notification_settings(
    family_id: str,
    family: Family = Depends(get_current_family),
    db: AsyncSession = Depends(get_db),
) -> NotificationSettingsResponse:
    if str(family.id) != family_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)

    result = await db.execute(
        select(NotificationSettings).where(NotificationSettings.family_id == family.id)
    )
    settings_row = result.scalar_one_or_none()
    if settings_row is None:
        # Families created before this feature landed won't have a row yet.
        settings_row = NotificationSettings(family_id=family.id)
        db.add(settings_row)
        await db.commit()
        await db.refresh(settings_row)
    return NotificationSettingsResponse.model_validate(settings_row)


@router.patch("/{family_id}/notification-settings", response_model=NotificationSettingsResponse)
async def update_notification_settings(
    family_id: str,
    body: NotificationSettingsUpdate,
    family: Family = Depends(get_current_family),
    db: AsyncSession = Depends(get_db),
) -> NotificationSettingsResponse:
    if str(family.id) != family_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)

    result = await db.execute(
        select(NotificationSettings).where(NotificationSettings.family_id == family.id)
    )
    settings_row = result.scalar_one_or_none()
    if settings_row is None:
        settings_row = NotificationSettings(family_id=family.id)
        db.add(settings_row)
        await db.flush()

    for field, value in body.model_dump(exclude_unset=True).items():
        setattr(settings_row, field, value)

    await db.commit()
    await db.refresh(settings_row)
    return NotificationSettingsResponse.model_validate(settings_row)
