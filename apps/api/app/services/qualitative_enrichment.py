import asyncio
import json
from typing import Optional

import sentry_sdk
from pydantic import BaseModel

from app.ai.client import get_openai_client
from app.ai.prompts.property_qualitative import QUALITATIVE_SYSTEM_PROMPT, QUALITATIVE_USER_PROMPT
from app.config import settings


class QualitativeScores(BaseModel):
    modernity: Optional[float] = None
    design_quality: Optional[float] = None
    indoor_outdoor_flow: Optional[float] = None
    home_office_suitability: Optional[float] = None
    entertaining_space: Optional[float] = None
    privacy: Optional[float] = None


_FALLBACK = QualitativeScores()
_DESCRIPTION_CHAR_LIMIT = 3000


async def enrich_qualitative(description: str, features: list[str]) -> QualitativeScores:
    if not settings.OPENAI_API_KEY or not description.strip():
        return _FALLBACK

    client = get_openai_client()
    features_text = ", ".join(features) if features else "None listed"
    prompt = QUALITATIVE_USER_PROMPT.format(
        description=description[:_DESCRIPTION_CHAR_LIMIT],
        features=features_text[:500],
    )

    try:
        response = await asyncio.wait_for(
            client.chat.completions.create(
                model=settings.OPENAI_MODEL_FAST,
                messages=[
                    {"role": "system", "content": QUALITATIVE_SYSTEM_PROMPT},
                    {"role": "user", "content": prompt},
                ],
                temperature=0.2,
                max_tokens=300,
                response_format={"type": "json_object"},
            ),
            timeout=30.0,
        )
        content = response.choices[0].message.content or "{}"
        raw = json.loads(content)
        return QualitativeScores(
            modernity=_clamp(raw.get("modernity")),
            design_quality=_clamp(raw.get("design_quality")),
            indoor_outdoor_flow=_clamp(raw.get("indoor_outdoor_flow")),
            home_office_suitability=_clamp(raw.get("home_office_suitability")),
            entertaining_space=_clamp(raw.get("entertaining_space")),
            privacy=_clamp(raw.get("privacy")),
        )
    except Exception as e:
        sentry_sdk.capture_exception(e)
        return _FALLBACK


def _clamp(val) -> Optional[float]:
    if val is None:
        return None
    try:
        return round(min(max(float(val), 0.0), 10.0), 1)
    except (ValueError, TypeError):
        return None
