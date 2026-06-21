import secrets
from datetime import datetime, timedelta, timezone
from typing import Optional
from uuid import UUID

import httpx
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.database import get_db
from app.dependencies import get_current_family, get_current_family_user, verify_clerk_jwt
from app.models.family import Family, FamilyInvite, FamilyMember, FamilyUser
from app.schemas.family import (
    FamilyMemberCreate,
    FamilyMemberResponse,
    FamilyResponse,
    FamilyUpdate,
    InviteCreateRequest,
)

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
    if not settings.RESEND_API_KEY:
        return
    invite_url = f"http://localhost:3000/invite/accept?token={token}"
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            await client.post(
                "https://api.resend.com/emails",
                headers={
                    "Authorization": f"Bearer {settings.RESEND_API_KEY}",
                    "Content-Type": "application/json",
                },
                json={
                    "from": "GC Move OS <noreply@gcmoveos.app>",
                    "to": [to_email],
                    "subject": f"Join {family_name} on GC Move OS",
                    "html": (
                        f"<p>{inviter_name} has invited you to join their family on GC Move OS.</p>"
                        f"<p><a href='{invite_url}'>Accept invitation</a></p>"
                        "<p>This link expires in 7 days.</p>"
                    ),
                },
            )
    except Exception:
        pass  # email is best-effort


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
