import uuid as _uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.dependencies import get_current_family, get_db
from app.models.family import Family
from app.models.intelligence import (
    EvaluationPerMember,
    EvaluationScore,
    PropertyEvaluation,
    Recommendation,
    RecommendationExplanation,
)
from app.models.property import Property
from app.schemas.evaluation import (
    EvaluationScoresResponse,
    FullEvaluationResponse,
    MemberCommentaryResponse,
    RecommendationExplanationResponse,
)

router = APIRouter(prefix="/evaluations", tags=["evaluations"])


@router.get("/{property_id}", response_model=FullEvaluationResponse)
async def get_evaluation(
    property_id: str,
    db: AsyncSession = Depends(get_db),
    current_family: Family = Depends(get_current_family),
):
    try:
        pid = _uuid.UUID(property_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid property ID")

    fid = current_family.id

    # Verify property belongs to this family
    prop_result = await db.execute(
        select(Property).where(
            Property.id == pid,
            Property.family_id == fid,
            Property.deleted_at.is_(None),
        )
    )
    prop = prop_result.scalar_one_or_none()
    if prop is None:
        raise HTTPException(status_code=404, detail="Property not found")

    # Load evaluation (most recent, current)
    eval_result = await db.execute(
        select(PropertyEvaluation)
        .where(
            PropertyEvaluation.property_id == pid,
            PropertyEvaluation.family_id == fid,
            PropertyEvaluation.is_current == True,
        )
        .options(
            selectinload(PropertyEvaluation.scores),
            selectinload(PropertyEvaluation.per_member),
            selectinload(PropertyEvaluation.recommendation).selectinload(
                Recommendation.explanations
            ),
        )
        .order_by(PropertyEvaluation.evaluated_at.desc())
        .limit(1)
    )
    evaluation = eval_result.scalar_one_or_none()

    if evaluation is None:
        raise HTTPException(status_code=404, detail="Evaluation not ready yet")

    scores_resp = None
    if evaluation.scores:
        s = evaluation.scores
        scores_resp = EvaluationScoresResponse.model_validate(s)

    per_member_resp = [
        MemberCommentaryResponse(
            member_id=pm.member_id,
            commentary=pm.commentary,
            key_positives=pm.key_positives,
            key_concerns=pm.key_concerns,
            fit_score=float(pm.fit_score) if pm.fit_score is not None else None,
        )
        for pm in (evaluation.per_member or [])
    ]

    rec = evaluation.recommendation
    explanations_resp = []
    rec_headline = None
    rec_summary = None
    rec_fit_score = None

    if rec:
        rec_headline = rec.headline
        rec_summary = rec.summary
        rec_fit_score = float(rec.family_fit_score) if rec.family_fit_score is not None else None
        explanations_resp = [
            RecommendationExplanationResponse(
                dimension=ex.dimension,
                explanation=ex.explanation,
                score=float(ex.score) if ex.score is not None else None,
            )
            for ex in (rec.explanations or [])
        ]

    return FullEvaluationResponse(
        evaluation_id=evaluation.id,
        property_id=evaluation.property_id,
        recommendation_level=evaluation.recommendation_level,
        meets_non_negotiables=evaluation.meets_non_negotiables,
        evaluated_at=evaluation.evaluated_at,
        confidence_score=float(evaluation.confidence_score),
        executive_summary=evaluation.executive_summary,
        community_narrative=evaluation.community_narrative,
        lifestyle_narrative=evaluation.lifestyle_narrative,
        school_narrative=evaluation.school_narrative,
        property_narrative=evaluation.property_narrative,
        financial_narrative=evaluation.financial_narrative,
        five_year_narrative=evaluation.five_year_narrative,
        deal_breakers_flagged=evaluation.deal_breakers_flagged,
        action_plan=evaluation.action_plan,
        scores=scores_resp,
        per_member=per_member_resp,
        recommendation_headline=rec_headline,
        recommendation_summary=rec_summary,
        family_fit_score=rec_fit_score,
        explanations=explanations_resp,
    )
