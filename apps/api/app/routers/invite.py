from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import verify_clerk_jwt
from app.models.family import Family, FamilyInvite, FamilyUser
from app.schemas.family import InviteAcceptRequest, InviteValidateResponse

router = APIRouter(prefix="/api/invite", tags=["invite"])


@router.get("/validate", response_model=InviteValidateResponse)
async def validate_invite(
    token: str = Query(...),
    db: AsyncSession = Depends(get_db),
) -> InviteValidateResponse:
    result = await db.execute(
        select(FamilyInvite, Family, FamilyUser)
        .join(Family, FamilyInvite.family_id == Family.id)
        .join(FamilyUser, FamilyInvite.invited_by_user_id == FamilyUser.id)
        .where(FamilyInvite.invite_token == token)
    )
    row = result.first()
    if row is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invite not found")

    invite, family, inviter = row

    if invite.status != "pending":
        raise HTTPException(status_code=status.HTTP_410_GONE, detail=f"Invite is {invite.status}")

    if invite.expires_at < datetime.now(timezone.utc):
        invite.status = "expired"
        await db.commit()
        raise HTTPException(status_code=status.HTTP_410_GONE, detail="Invite has expired")

    return InviteValidateResponse(
        family_name=family.display_name,
        inviter_name=inviter.display_name,
        email=invite.email,
        role=invite.role,
    )


@router.post("/accept", status_code=status.HTTP_201_CREATED)
async def accept_invite(
    body: InviteAcceptRequest,
    clerk_user_id: str = Depends(verify_clerk_jwt),
    db: AsyncSession = Depends(get_db),
) -> dict:
    existing = await db.execute(
        select(FamilyUser).where(FamilyUser.clerk_user_id == clerk_user_id)
    )
    if existing.scalar_one_or_none() is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User already belongs to a family.",
        )

    result = await db.execute(
        select(FamilyInvite).where(FamilyInvite.invite_token == body.invite_token)
    )
    invite = result.scalar_one_or_none()
    if invite is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invite not found")

    if invite.status != "pending":
        raise HTTPException(status_code=status.HTTP_410_GONE, detail=f"Invite is {invite.status}")

    if invite.expires_at < datetime.now(timezone.utc):
        invite.status = "expired"
        await db.commit()
        raise HTTPException(status_code=status.HTTP_410_GONE, detail="Invite has expired")

    family_user = FamilyUser(
        family_id=invite.family_id,
        clerk_user_id=clerk_user_id,
        role=invite.role,
        display_name=invite.email.split("@")[0],
        email=invite.email,
    )
    db.add(family_user)

    invite.status = "accepted"
    invite.accepted_at = datetime.now(timezone.utc)

    await db.flush()  # writes family_user first so FK is satisfied
    invite.accepted_by_user_id = family_user.id
    await db.commit()

    return {"message": "Invite accepted", "family_id": str(invite.family_id)}
