import logging
import uuid as _uuid
from typing import Optional

import sentry_sdk
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.database import AsyncSessionLocal
from app.models.family import Family, FamilyMember, FamilyPreference
from app.models.intelligence import (
    EvaluationPerMember,
    EvaluationScore,
    PropertyEvaluation,
    Recommendation,
    RecommendationExplanation,
)
from app.models.location import School, Suburb, SuburbLifestyleAsset, SuburbMetric
from app.models.property import Property, PropertyFeature
from app.services.community_scoring import calculate_community_score
from app.services.family_fit import (
    NEUTRAL_FINANCIAL,
    RECOMMENDATION_LABELS,
    calculate_family_fit,
    calculate_five_year_fit,
    determine_recommendation,
)
from app.services.lifestyle_scoring import calculate_lifestyle_score
from app.services.non_negotiables import check_non_negotiables
from app.services.property_scoring import calculate_property_score
from app.services.recommendation_service import generate_recommendation
from app.services.risk_scoring import calculate_risk_score
from app.services.school_scoring import calculate_school_score
from app.services.travel_time import calculate_travel_times

logger = logging.getLogger(__name__)


async def run_evaluation(property_id: str, family_id: str) -> None:
    try:
        async with AsyncSessionLocal() as db:
            await _evaluate(property_id, family_id, db)
    except Exception as e:
        sentry_sdk.capture_exception(e)
        logger.error("Evaluation pipeline failed for property %s: %s", property_id, e)
        async with AsyncSessionLocal() as db:
            await _mark_failed(property_id, db)


async def _evaluate(property_id: str, family_id: str, db) -> None:
    pid = _uuid.UUID(property_id)
    fid = _uuid.UUID(family_id)

    # ── 1. Load property ──────────────────────────────────────────────────────
    prop_result = await db.execute(
        select(Property)
        .where(Property.id == pid, Property.family_id == fid, Property.deleted_at.is_(None))
        .options(selectinload(Property.features), selectinload(Property.images))
    )
    prop: Optional[Property] = prop_result.scalar_one_or_none()
    if prop is None:
        logger.warning("Property %s not found for evaluation", property_id)
        return

    # ── 2. Load family + members + preferences ────────────────────────────────
    family_result = await db.execute(
        select(Family)
        .where(Family.id == fid)
        .options(
            selectinload(Family.members),
            selectinload(Family.preferences),
        )
    )
    family: Optional[Family] = family_result.scalar_one_or_none()
    if family is None:
        logger.warning("Family %s not found for evaluation", family_id)
        return

    members: list[FamilyMember] = [m for m in family.members if m.deleted_at is None]
    preferences: list[FamilyPreference] = [p for p in family.preferences if p.deleted_at is None]
    features: list[PropertyFeature] = list(prop.features)

    # ── 3. Travel times ───────────────────────────────────────────────────────
    if prop.latitude is not None and prop.longitude is not None:
        burleigh_mins, beach_mins = await calculate_travel_times(
            float(prop.latitude), float(prop.longitude), property_id
        )
        if burleigh_mins is not None:
            db.add(PropertyFeature(
                family_id=fid,
                property_id=pid,
                feature_key="burleigh_drive_minutes",
                feature_value=str(burleigh_mins),
                feature_type="numeric",
                source="inferred",
                confidence=0.95,
            ))
        if beach_mins is not None:
            db.add(PropertyFeature(
                family_id=fid,
                property_id=pid,
                feature_key="beach_drive_minutes",
                feature_value=str(beach_mins),
                feature_type="numeric",
                source="inferred",
                confidence=0.95,
            ))
        await db.flush()
        # Reload features to include the travel time rows we just added
        feat_result = await db.execute(
            select(PropertyFeature)
            .where(PropertyFeature.property_id == pid)
        )
        features = list(feat_result.scalars().all())
    else:
        burleigh_mins = beach_mins = None

    # ── 4. Non-negotiable check ───────────────────────────────────────────────
    nn_result = check_non_negotiables(prop, family, features)
    meets_non_negotiables = nn_result.passed

    if not nn_result.passed:
        db.add(PropertyFeature(
            family_id=fid,
            property_id=pid,
            feature_key="filter_reason",
            feature_value=nn_result.failure_reason or "Failed non-negotiable check",
            feature_type="text",
            source="inferred",
            confidence=1.0,
        ))

    # ── 5. Load suburb data ───────────────────────────────────────────────────
    suburb_metric: Optional[SuburbMetric] = None
    suburb_lifestyle: Optional[SuburbLifestyleAsset] = None

    if prop.suburb_id is not None:
        suburb_result = await db.execute(
            select(Suburb)
            .where(Suburb.id == prop.suburb_id)
            .options(
                selectinload(Suburb.metrics),
                selectinload(Suburb.lifestyle_assets),
            )
        )
        suburb = suburb_result.scalar_one_or_none()
        if suburb:
            suburb_metric = suburb.metrics
            suburb_lifestyle = suburb.lifestyle_assets

    # ── 6. Score each dimension ───────────────────────────────────────────────
    community = calculate_community_score(suburb_metric)
    lifestyle = calculate_lifestyle_score(features, suburb_lifestyle)

    prop_lat = float(prop.latitude) if prop.latitude is not None else None
    prop_lng = float(prop.longitude) if prop.longitude is not None else None
    school = await calculate_school_score(prop.suburb_id, prop_lat, prop_lng, db)

    property_result = calculate_property_score(features, prop.land_area_sqm)
    risk = calculate_risk_score(prop, suburb_metric, features, family)

    financial = NEUTRAL_FINANCIAL  # disabled until budget set (OQ-001)

    # ── 7. Confidence ─────────────────────────────────────────────────────────
    confidence = 1.0
    if prop.suburb_id is None:
        confidence -= 0.15
    if not school.matched_schools:
        confidence -= 0.10
    if burleigh_mins is None and beach_mins is None:
        confidence -= 0.10
    if not prop.images:
        confidence -= 0.05
    if prop.data_quality_score is not None and prop.data_quality_score < 50:
        confidence -= 0.05
    confidence = round(max(0.0, confidence), 2)

    # ── 8. Family fit + recommendation ───────────────────────────────────────
    family_fit = calculate_family_fit(
        community.community_score,
        lifestyle.lifestyle_score,
        school.school_score,
        property_result.property_score,
        financial,
        family,
    )
    five_year = calculate_five_year_fit(
        community.community_score,
        lifestyle.lifestyle_score,
        school.school_score,
        property_result.property_score,
        financial,
        risk.risk_score,
    )
    recommendation_level = determine_recommendation(
        family_fit, confidence, risk.has_critical_risk, meets_non_negotiables
    )

    # ── 9. AI narrative ───────────────────────────────────────────────────────
    ai_output = await generate_recommendation(
        prop=prop,
        family=family,
        members=members,
        preferences=preferences,
        community=community,
        lifestyle=lifestyle,
        school=school,
        property_score=property_result,
        risk=risk,
        family_fit_score=family_fit,
        five_year_fit_score=five_year,
        confidence=confidence,
        recommendation_level=recommendation_level,
    )

    # ── 10. Persist PropertyEvaluation ────────────────────────────────────────
    eval_rec = PropertyEvaluation(
        family_id=fid,
        property_id=pid,
        suburb_id=prop.suburb_id,
        confidence_score=confidence,
        recommendation_level=recommendation_level,
        meets_non_negotiables=meets_non_negotiables,
        executive_summary=ai_output.executive_summary,
        community_narrative=ai_output.community_narrative,
        lifestyle_narrative=ai_output.lifestyle_narrative,
        school_narrative=ai_output.school_narrative,
        property_narrative=ai_output.property_narrative,
        financial_narrative=ai_output.financial_narrative,
        five_year_narrative=ai_output.five_year_narrative,
        deal_breakers_flagged=[r.description for r in risk.risks if r.level == "critical"] or None,
        action_plan={
            "what_to_verify": ai_output.what_to_verify,
            "main_trade_off": ai_output.main_trade_off,
            "next_action": ai_output.next_action,
        },
    )
    db.add(eval_rec)
    await db.flush()

    # ── 11. Persist EvaluationScore ───────────────────────────────────────────
    db.add(EvaluationScore(
        evaluation_id=eval_rec.id,
        family_id=fid,
        community_score=community.community_score,
        lifestyle_score=lifestyle.lifestyle_score,
        school_score=school.school_score,
        property_score=property_result.property_score,
        financial_score=None,
        risk_score=risk.risk_score,
        family_fit_score=family_fit,
        five_year_fit_score=five_year,
        owner_occupier_score=community.owner_occupier,
        family_density_score=community.family_density,
        educational_attainment_score=community.educational_attainment,
        median_income_score=community.median_income,
        crime_score=community.crime,
        community_engagement_score=community.community_engagement,
        burleigh_access_score=lifestyle.burleigh_access,
        beach_access_score=lifestyle.beach_access,
        wellness_score=lifestyle.wellness,
        cafe_dining_score=lifestyle.cafe_dining,
        outdoor_recreation_score=lifestyle.outdoor_recreation,
        shopping_score=lifestyle.shopping,
        wellbeing_score=school.wellbeing,
        parent_community_score=school.parent_community,
        academic_outcomes_score=school.academic,
        school_commute_score=school.commute,
        extracurricular_score=school.extracurricular,
        school_pathway_score=school.pathway,
        modernity_score=property_result.modernity,
        design_quality_score=property_result.design_quality,
        indoor_outdoor_flow_score=property_result.indoor_outdoor_flow,
        pool_quality_score=property_result.pool,
        home_office_score=property_result.home_office,
        entertaining_space_score=property_result.entertaining_space,
        privacy_score=property_result.privacy,
        block_utility_score=property_result.block_utility,
        weights_snapshot={
            "community": float(family.weight_community),
            "lifestyle": float(family.weight_lifestyle),
            "school": float(family.weight_school),
            "property": float(family.weight_property),
            "financial": float(family.weight_financial),
        },
    ))

    # ── 12. Persist EvaluationPerMember ──────────────────────────────────────
    member_by_name = {m.first_name.lower(): m for m in members}
    for cm in ai_output.per_member:
        matched = member_by_name.get(cm.member_name.lower())
        if matched is None:
            continue
        db.add(EvaluationPerMember(
            evaluation_id=eval_rec.id,
            family_id=fid,
            member_id=matched.id,
            commentary=cm.commentary,
            key_positives=cm.key_positives or None,
            key_concerns=cm.key_concerns or None,
        ))

    # ── 13. Persist Recommendation ────────────────────────────────────────────
    existing_rec_result = await db.execute(
        select(Recommendation).where(
            Recommendation.family_id == fid,
            Recommendation.property_id == pid,
        )
    )
    existing_rec = existing_rec_result.scalar_one_or_none()

    label = RECOMMENDATION_LABELS.get(recommendation_level, recommendation_level)
    if existing_rec:
        existing_rec.evaluation_id = eval_rec.id
        existing_rec.family_fit_score = family_fit
        existing_rec.headline = label
        existing_rec.summary = ai_output.next_action
    else:
        rec = Recommendation(
            family_id=fid,
            property_id=pid,
            evaluation_id=eval_rec.id,
            family_fit_score=family_fit,
            headline=label,
            summary=ai_output.next_action,
            status="active",
        )
        db.add(rec)
        await db.flush()
        existing_rec = rec

    # ── 14. Persist RecommendationExplanation rows ────────────────────────────
    explanations = [
        ("community", ai_output.community_narrative, community.community_score),
        ("lifestyle", ai_output.lifestyle_narrative, lifestyle.lifestyle_score),
        ("school", ai_output.school_narrative, school.school_score),
        ("property", ai_output.property_narrative, property_result.property_score),
        ("financial", ai_output.financial_narrative, None),
        ("family_fit", ai_output.executive_summary, family_fit),
        ("risk", "; ".join(r.description for r in risk.risks) or "No significant risks", risk.risk_score),
    ]
    for dimension, explanation, score in explanations:
        db.add(RecommendationExplanation(
            recommendation_id=existing_rec.id,
            family_id=fid,
            dimension=dimension,
            explanation=explanation or "",
            score=score,
        ))

    # ── 15. Update property status ────────────────────────────────────────────
    prop.status = "filtered" if not meets_non_negotiables else "evaluated"
    await db.commit()
    logger.info(
        "Evaluation complete for property %s — %s (fit=%.1f, confidence=%.0f%%)",
        property_id,
        recommendation_level,
        family_fit,
        confidence * 100,
    )


async def _mark_failed(property_id: str, db) -> None:
    try:
        pid = _uuid.UUID(property_id)
        result = await db.execute(
            select(Property).where(Property.id == pid)
        )
        prop = result.scalar_one_or_none()
        if prop:
            prop.status = "failed"
            await db.commit()
    except Exception as e:
        sentry_sdk.capture_exception(e)
