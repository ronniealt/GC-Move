from __future__ import annotations
from datetime import date, datetime, time
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, ConfigDict, EmailStr


class FamilyCreate(BaseModel):
    display_name: str
    primary_suburb_target: Optional[str] = None
    budget_min_aud: Optional[int] = None
    budget_max_aud: Optional[int] = None
    target_move_date: Optional[date] = None


class FamilyUpdate(BaseModel):
    display_name: Optional[str] = None
    primary_suburb_target: Optional[str] = None
    budget_min_aud: Optional[int] = None
    budget_max_aud: Optional[int] = None
    target_move_date: Optional[date] = None
    target_move_timeline: Optional[str] = None
    onboarding_completed: Optional[bool] = None
    weight_community: Optional[float] = None
    weight_lifestyle: Optional[float] = None
    weight_school: Optional[float] = None
    weight_property: Optional[float] = None
    weight_financial: Optional[float] = None


class FamilyResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    display_name: str
    primary_suburb_target: Optional[str]
    budget_min_aud: Optional[int]
    budget_max_aud: Optional[int]
    target_move_date: Optional[date]
    target_move_timeline: Optional[str]
    is_active: bool
    onboarding_completed: bool
    scoring_model_version: str
    weight_community: float
    weight_lifestyle: float
    weight_school: float
    weight_property: float
    weight_financial: float
    created_at: datetime


class NonNegotiablesSetRequest(BaseModel):
    labels: list[str]
    property_type: Optional[str] = None  # "house" | "townhouse" | "unit" | "acreage" | "any" | None


class FamilyNonNegotiableResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    criterion_key: str
    comparator: str
    value: str
    label: Optional[str]
    source: str


class SuburbTargetsSetRequest(BaseModel):
    suburb_ids: list[UUID]


class FamilySuburbsResponse(BaseModel):
    suburb_ids: list[UUID]


class NotificationSettingsUpdate(BaseModel):
    email_new_evaluation: Optional[bool] = None
    email_rank_change: Optional[bool] = None
    email_daily_digest: Optional[bool] = None
    email_inspection_reminder: Optional[bool] = None
    push_enabled: Optional[bool] = None
    digest_time: Optional[time] = None


class NotificationSettingsResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    email_new_evaluation: bool
    email_rank_change: bool
    email_daily_digest: bool
    email_inspection_reminder: bool
    push_enabled: bool
    digest_time: Optional[time]


class FamilyMemberCreate(BaseModel):
    first_name: str
    role: str
    age: Optional[int] = None
    birth_year: Optional[int] = None
    notes: Optional[str] = None
    avatar_emoji: Optional[str] = "👤"


class FamilyMemberResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    family_id: UUID
    first_name: str
    role: str
    age: Optional[int]
    birth_year: Optional[int]
    notes: Optional[str]
    avatar_emoji: Optional[str]
    created_at: datetime


class InviteCreateRequest(BaseModel):
    email: EmailStr
    role: str = "member"


class InviteValidateResponse(BaseModel):
    family_name: str
    inviter_name: str
    email: str
    role: str


class InviteAcceptRequest(BaseModel):
    invite_token: str
