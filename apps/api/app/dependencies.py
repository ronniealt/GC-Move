from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db

bearer = HTTPBearer()


async def verify_clerk_jwt(
    credentials: HTTPAuthorizationCredentials = Depends(bearer),
) -> str:
    """Verify Clerk JWT and return clerk_user_id. Full implementation in Task 0.4."""
    # TODO: implement Clerk JWT verification once CLERK_SECRET_KEY is configured
    token = credentials.credentials
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    return token


async def get_current_user_and_family(
    clerk_user_id: str = Depends(verify_clerk_jwt),
    db: AsyncSession = Depends(get_db),
):
    """Resolve clerk_user_id to (FamilyUser, Family). Full implementation in Task 0.4."""
    # TODO: implement once DB models and Clerk integration are in place
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED)
