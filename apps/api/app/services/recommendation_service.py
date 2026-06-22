import asyncio
import json
import logging
from dataclasses import dataclass, field
from typing import Optional

import sentry_sdk

from app.ai.client import get_openai_client
from app.ai.prompts.recommendation import RECOMMENDATION_SYSTEM_PROMPT, RECOMMENDATION_USER_PROMPT
from app.config import settings
from app.models.family import Family, FamilyMember, FamilyPreference
from app.models.property import Property
from app.services.community_scoring import CommunityScoreResult
from app.services.family_fit import RECOMMENDATION_LABELS
from app.services.lifestyle_scoring import LifestyleScoreResult
from app.services.property_scoring import PropertyScoreResult
from app.services.risk_scoring import Risk, RiskResult
from app.services.school_scoring import SchoolScoreResult

logger = logging.getLogger(__name__)

_TIMEOUT_SECS = 45.0


@dataclass
class MemberCommentary:
    member_name: str
    commentary: str
    key_positives: list[str] = field(default_factory=list)
    key_concerns: list[str] = field(default_factory=list)


@dataclass
class RecommendationOutput:
    executive_summary: str
    community_narrative: str
    lifestyle_narrative: str
    school_narrative: str
    property_narrative: str
    financial_narrative: str
    five_year_narrative: str
    what_to_verify: list[str]
    main_trade_off: str
    next_action: str
    per_member: list[MemberCommentary]


async def generate_recommendation(
    prop: Property,
    family: Family,
    members: list[FamilyMember],
    preferences: list[FamilyPreference],
    community: CommunityScoreResult,
    lifestyle: LifestyleScoreResult,
    school: SchoolScoreResult,
    property_score: PropertyScoreResult,
    risk: RiskResult,
    family_fit_score: float,
    five_year_fit_score: float,
    confidence: float,
    recommendation_level: str,
) -> RecommendationOutput:
    if not settings.OPENAI_API_KEY:
        return _fallback(prop, family_fit_score, recommendation_level, members)

    prompt = _build_prompt(
        prop, family, members, preferences,
        community, lifestyle, school, property_score,
        risk, family_fit_score, confidence, recommendation_level,
    )

    try:
        raw = await asyncio.wait_for(
            _call_openai(prompt),
            timeout=_TIMEOUT_SECS,
        )
        return _parse(raw, members)
    except Exception as e:
        sentry_sdk.capture_exception(e)
        logger.warning("Recommendation AI call failed for property %s: %s", prop.id, e)
        return _fallback(prop, family_fit_score, recommendation_level, members)


async def _call_openai(prompt: str) -> str:
    client = get_openai_client()
    response = await client.chat.completions.create(
        model=settings.OPENAI_MODEL_MAIN,
        messages=[
            {"role": "system", "content": RECOMMENDATION_SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ],
        temperature=0.4,
        max_tokens=2000,
        response_format={"type": "json_object"},
    )
    return response.choices[0].message.content or "{}"


def _build_prompt(
    prop: Property,
    family: Family,
    members: list[FamilyMember],
    preferences: list[FamilyPreference],
    community: CommunityScoreResult,
    lifestyle: LifestyleScoreResult,
    school: SchoolScoreResult,
    property_score: PropertyScoreResult,
    risk: RiskResult,
    family_fit: float,
    confidence: float,
    recommendation_level: str,
) -> str:
    members_text = "\n".join(
        f"- {m.first_name} ({m.role}, age {m.age or 'unknown'})"
        for m in members
    )

    address = f"{prop.address_street}, {prop.address_suburb}"
    price = _format_price(prop)
    land = f"{prop.land_area_sqm} sqm" if prop.land_area_sqm else "unknown"

    risks_text = (
        "\n".join(f"- [{r.level.upper()}] {r.description}" for r in risk.risks)
        or "No significant risks identified"
    )

    top_prefs = sorted(
        [p for p in preferences if p.status in ("Confirmed", "Manual")],
        key=lambda p: float(p.current_weight),
        reverse=True,
    )[:5]
    preferences_text = (
        "\n".join(f"- {p.attribute} (weight {p.current_weight})" for p in top_prefs)
        or "No confirmed preferences yet"
    )

    return RECOMMENDATION_USER_PROMPT.format(
        family_name=family.display_name,
        members_text=members_text,
        address=address,
        suburb=prop.address_suburb,
        price=price,
        property_type=prop.property_type,
        bedrooms=prop.bedrooms or "?",
        bathrooms=prop.bathrooms or "?",
        land_area=land,
        community_score=community.community_score,
        lifestyle_score=lifestyle.lifestyle_score,
        school_score=school.school_score,
        property_score=property_score.property_score,
        financial_score="N/A (budget not set)",
        family_fit_score=family_fit,
        risk_score=risk.risk_score,
        confidence=f"{confidence:.0%}",
        recommendation_level=RECOMMENDATION_LABELS.get(recommendation_level, recommendation_level),
        risks_text=risks_text,
        preferences_text=preferences_text,
    )


def _parse(raw: str, members: list[FamilyMember]) -> RecommendationOutput:
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        raise ValueError("OpenAI returned invalid JSON")

    per_member_raw = data.get("per_member_commentary") or []
    per_member = [
        MemberCommentary(
            member_name=item.get("member_name", ""),
            commentary=item.get("commentary", ""),
            key_positives=item.get("key_positives") or [],
            key_concerns=item.get("key_concerns") or [],
        )
        for item in per_member_raw
        if isinstance(item, dict)
    ]

    return RecommendationOutput(
        executive_summary=data.get("executive_summary", ""),
        community_narrative=data.get("community_narrative", ""),
        lifestyle_narrative=data.get("lifestyle_narrative", ""),
        school_narrative=data.get("school_narrative", ""),
        property_narrative=data.get("property_narrative", ""),
        financial_narrative=data.get("financial_narrative", ""),
        five_year_narrative=data.get("five_year_narrative", ""),
        what_to_verify=data.get("what_to_verify") or [],
        main_trade_off=data.get("main_trade_off", ""),
        next_action=data.get("next_action", ""),
        per_member=per_member,
    )


def _fallback(
    prop: Property,
    family_fit: float,
    recommendation_level: str,
    members: list[FamilyMember],
) -> RecommendationOutput:
    label = RECOMMENDATION_LABELS.get(recommendation_level, recommendation_level)
    address = f"{prop.address_street}, {prop.address_suburb}"
    summary = (
        f"Recommendation: {label}. "
        f"This property at {address} has been evaluated with a family fit score of {family_fit}/10. "
        "Full narrative unavailable — AI service temporarily offline."
    )
    return RecommendationOutput(
        executive_summary=summary,
        community_narrative="Community data evaluated. See scores above.",
        lifestyle_narrative="Lifestyle data evaluated. See scores above.",
        school_narrative="School data evaluated. See scores above.",
        property_narrative="Property data evaluated. See scores above.",
        financial_narrative="Financial scoring pending budget configuration.",
        five_year_narrative="Five-year prediction unavailable — AI service temporarily offline.",
        what_to_verify=["Verify key property details during inspection"],
        main_trade_off="See scores for trade-off analysis.",
        next_action="Review the scores and contact your agent with questions.",
        per_member=[
            MemberCommentary(
                member_name=m.first_name,
                commentary="Individual commentary unavailable — AI service temporarily offline.",
                key_positives=[],
                key_concerns=[],
            )
            for m in members
        ],
    )


def _format_price(prop: Property) -> str:
    if prop.listing_price_aud:
        return f"${prop.listing_price_aud:,}"
    if prop.price_range_low_aud and prop.price_range_high_aud:
        return f"${prop.price_range_low_aud:,} – ${prop.price_range_high_aud:,}"
    if prop.price_range_high_aud:
        return f"Up to ${prop.price_range_high_aud:,}"
    return "Price not listed"
