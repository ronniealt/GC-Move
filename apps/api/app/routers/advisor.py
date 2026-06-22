from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_current_family, get_db
from app.models.family import Family
from app.schemas.advisor import AdvisorChatRequest, AdvisorHistoryResponse, AdvisorMessageResponse
from app.services import ai_advisor

router = APIRouter(prefix="/api/advisor", tags=["advisor"])


@router.post("/chat", response_model=AdvisorMessageResponse)
async def chat(
    body: AdvisorChatRequest,
    family: Family = Depends(get_current_family),
    db: AsyncSession = Depends(get_db),
) -> AdvisorMessageResponse:
    assistant_msg = await ai_advisor.send_message(
        db=db,
        family=family,
        message=body.message,
        property_id=body.property_id,
    )
    return AdvisorMessageResponse.model_validate(assistant_msg)


@router.get("/history", response_model=AdvisorHistoryResponse)
async def history(
    family: Family = Depends(get_current_family),
    db: AsyncSession = Depends(get_db),
) -> AdvisorHistoryResponse:
    thread_id, messages = await ai_advisor.get_history(db=db, family=family)
    if thread_id is None:
        return AdvisorHistoryResponse(thread_id=None, messages=[])
    return AdvisorHistoryResponse(
        thread_id=thread_id,
        messages=[AdvisorMessageResponse.model_validate(m) for m in messages],
    )
