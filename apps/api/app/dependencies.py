from datetime import datetime, timezone

import httpx
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwk, jwt
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.family import Family, FamilyUser

bearer = HTTPBearer()

_jwks_by_issuer: dict[str, list[dict]] = {}
_jwks_fetched_at: datetime | None = None
_JWKS_TTL_SECONDS = 300


async def _get_jwks(issuer: str) -> list[dict]:
    global _jwks_fetched_at, _jwks_by_issuer

    now = datetime.now(timezone.utc)
    cache_valid = _jwks_fetched_at and (now - _jwks_fetched_at).total_seconds() < _JWKS_TTL_SECONDS
    if cache_valid and issuer in _jwks_by_issuer:
        return _jwks_by_issuer[issuer]

    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.get(f"{issuer}/.well-known/jwks.json")
            resp.raise_for_status()
            keys = resp.json().get("keys", [])
    except Exception:
        # Return cached keys on fetch failure rather than locking out users
        return _jwks_by_issuer.get(issuer, [])

    _jwks_by_issuer[issuer] = keys
    _jwks_fetched_at = now  # timezone-aware (UTC)
    return keys


async def verify_clerk_jwt(
    credentials: HTTPAuthorizationCredentials = Depends(bearer),
) -> str:
    """Verify Clerk RS256 JWT and return clerk_user_id (sub claim)."""
    token = credentials.credentials

    try:
        unverified_header = jwt.get_unverified_header(token)
        unverified_claims = jwt.get_unverified_claims(token)
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token format")

    issuer: str = unverified_claims.get("iss", "")
    kid: str = unverified_header.get("kid", "")

    if not issuer:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing issuer in token")

    keys = await _get_jwks(issuer)
    matching_key = next((k for k in keys if k.get("kid") == kid), None)
    if matching_key is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unknown signing key")

    try:
        public_key = jwk.construct(matching_key)
        claims = jwt.decode(token, public_key, algorithms=["RS256"])
        clerk_user_id: str = claims["sub"]
        return clerk_user_id
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token")


async def get_current_user_and_family(
    clerk_user_id: str = Depends(verify_clerk_jwt),
    db: AsyncSession = Depends(get_db),
) -> tuple[FamilyUser, Family]:
    result = await db.execute(
        select(FamilyUser, Family)
        .join(Family, FamilyUser.family_id == Family.id)
        .where(
            FamilyUser.clerk_user_id == clerk_user_id,
            Family.deleted_at.is_(None),
            Family.is_active.is_(True),
        )
    )
    row = result.first()
    if row is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No family found for this user. Complete onboarding first.",
        )
    family_user, family = row
    return family_user, family


async def get_current_family(
    pair: tuple[FamilyUser, Family] = Depends(get_current_user_and_family),
) -> Family:
    return pair[1]


async def get_current_family_user(
    pair: tuple[FamilyUser, Family] = Depends(get_current_user_and_family),
) -> FamilyUser:
    return pair[0]
