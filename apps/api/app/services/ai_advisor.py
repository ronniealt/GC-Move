from __future__ import annotations

import asyncio
import logging
from datetime import datetime, timezone
from typing import Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.ai.client import get_openai_client
from app.ai.prompts.advisor import build_system_prompt
from app.config import settings
from app.models.family import Family, FamilyMember, FamilyPreference
from app.models.intelligence import PropertyEvaluation
from app.models.operational import AIAdvisorMessage, AIAdvisorThread
from app.models.property import Property

logger = logging.getLogger(__name__)

FALLBACK_RESPONSE = (
    "I'm having trouble connecting right now. Please try again in a moment — "
    "I'll have your full family context ready when you do."
)


async def _get_or_create_thread(db: AsyncSession, family_id: UUID) -> AIAdvisorThread:
    result = await db.execute(
        select(AIAdvisorThread).where(
            AIAdvisorThread.family_id == family_id,
            AIAdvisorThread.is_active.is_(True),
        )
    )
    thread = result.scalar_one_or_none()
    if thread is None:
        thread = AIAdvisorThread(
            family_id=family_id,
            openai_thread_id=f"gcmove_{family_id}",
            is_active=True,
            message_count=0,
        )
        db.add(thread)
        await db.flush()
    return thread


async def _load_family_context(
    db: AsyncSession, family_id: UUID
) -> tuple[Family, list[FamilyMember], list[FamilyPreference]]:
    family_result = await db.execute(
        select(Family)
        .options(selectinload(Family.members))
        .where(Family.id == family_id)
    )
    family = family_result.scalar_one()

    pref_result = await db.execute(
        select(FamilyPreference)
        .where(
            FamilyPreference.family_id == family_id,
            FamilyPreference.status.in_(["Confirmed", "Emerging"]),
        )
        .order_by(FamilyPreference.current_weight.desc())
        .limit(10)
    )
    preferences = list(pref_result.scalars().all())

    return family, family.members, preferences


async def _load_property_context(
    db: AsyncSession, family_id: UUID, property_id: UUID
) -> Optional[str]:
    prop_result = await db.execute(
        select(Property).where(
            Property.id == property_id,
            Property.family_id == family_id,
        )
    )
    prop = prop_result.scalar_one_or_none()
    if prop is None:
        return None

    eval_result = await db.execute(
        select(PropertyEvaluation)
        .options(selectinload(PropertyEvaluation.scores))
        .where(
            PropertyEvaluation.property_id == property_id,
            PropertyEvaluation.family_id == family_id,
            PropertyEvaluation.is_current.is_(True),
        )
    )
    evaluation = eval_result.scalar_one_or_none()

    lines: list[str] = [
        f"\nACTIVE PROPERTY CONTEXT — {prop.address_street}, {prop.address_suburb}:",
    ]
    if prop.listing_price_aud:
        lines.append(f"  Price: ${prop.listing_price_aud:,}")
    bed = prop.bedrooms or "?"
    bath = prop.bathrooms or "?"
    car = prop.car_spaces or "?"
    lines.append(f"  {bed}bd / {bath}ba / {car} car")
    if prop.land_area_sqm:
        lines.append(f"  Land: {prop.land_area_sqm}m²")
    if prop.property_type:
        lines.append(f"  Type: {prop.property_type}")

    if evaluation:
        s = evaluation.scores
        if s:
            lines.append(
                f"  Scores — Family Fit: {s.family_fit_score} | "
                f"Community: {s.community_score} | Lifestyle: {s.lifestyle_score} | "
                f"Schools: {s.school_score} | Property: {s.property_score}"
            )
        if evaluation.executive_summary:
            lines.append(f"  AI Summary: {evaluation.executive_summary}")
        if evaluation.deal_breakers_flagged:
            lines.append(f"  Risks: {', '.join(evaluation.deal_breakers_flagged)}")

    return "\n".join(lines)


async def _load_history(
    db: AsyncSession, thread_id: UUID, family_id: UUID, limit: int = 20
) -> list[AIAdvisorMessage]:
    result = await db.execute(
        select(AIAdvisorMessage)
        .where(
            AIAdvisorMessage.thread_id == thread_id,
            AIAdvisorMessage.family_id == family_id,
            AIAdvisorMessage.role.in_(["user", "assistant"]),
        )
        .order_by(AIAdvisorMessage.created_at.asc())
        .limit(limit)
    )
    return list(result.scalars().all())


async def send_message(
    db: AsyncSession,
    family: Family,
    message: str,
    property_id: Optional[UUID] = None,
) -> AIAdvisorMessage:
    thread = await _get_or_create_thread(db, family.id)
    loaded_family, members, preferences = await _load_family_context(db, family.id)

    property_context: Optional[str] = None
    if property_id:
        property_context = await _load_property_context(db, family.id, property_id)

    system_prompt = build_system_prompt(loaded_family, members, preferences, property_context)
    history = await _load_history(db, thread.id, family.id)

    openai_messages: list[dict] = [{"role": "system", "content": system_prompt}]
    for msg in history:
        openai_messages.append({"role": msg.role, "content": msg.content})
    openai_messages.append({"role": "user", "content": message})

    user_msg = AIAdvisorMessage(
        family_id=family.id,
        thread_id=thread.id,
        role="user",
        content=message,
        property_id=property_id,
    )
    db.add(user_msg)
    await db.flush()

    reply_content = FALLBACK_RESPONSE
    tokens_used: Optional[int] = None

    try:
        client = get_openai_client()
        response = await asyncio.wait_for(
            client.chat.completions.create(
                model=settings.OPENAI_MODEL_MAIN,
                messages=openai_messages,  # type: ignore[arg-type]
                max_tokens=1000,
                temperature=0.7,
            ),
            timeout=30.0,
        )
        reply_content = response.choices[0].message.content or FALLBACK_RESPONSE
        if response.usage:
            tokens_used = response.usage.total_tokens
    except Exception as exc:
        logger.error("AI advisor error for family %s: %s", family.id, exc)

    assistant_msg = AIAdvisorMessage(
        family_id=family.id,
        thread_id=thread.id,
        role="assistant",
        content=reply_content,
        property_id=property_id,
        tokens_used=tokens_used,
    )
    db.add(assistant_msg)

    thread.message_count = (thread.message_count or 0) + 2
    thread.last_message_at = datetime.now(timezone.utc)

    await db.flush()
    return assistant_msg


async def get_history(
    db: AsyncSession, family: Family
) -> tuple[Optional[UUID], list[AIAdvisorMessage]]:
    result = await db.execute(
        select(AIAdvisorThread).where(
            AIAdvisorThread.family_id == family.id,
            AIAdvisorThread.is_active.is_(True),
        )
    )
    thread = result.scalar_one_or_none()
    if thread is None:
        return None, []

    messages = await _load_history(db, thread.id, family.id, limit=50)
    return thread.id, messages
