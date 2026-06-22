from __future__ import annotations
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, ConfigDict, computed_field


class SuburbMetricResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    owner_occupier_rate: Optional[float] = None
    owner_occupier_score: Optional[float] = None
    family_density_pct: Optional[float] = None
    family_density_score: Optional[float] = None
    educational_attainment_pct: Optional[float] = None
    educational_attainment_score: Optional[float] = None
    median_weekly_household_income_aud: Optional[int] = None
    median_income_score: Optional[float] = None
    crime_index: Optional[float] = None
    crime_score: Optional[float] = None
    community_engagement_score: Optional[float] = None
    community_score: Optional[float] = None


class SuburbLifestyleResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    cafe_restaurant_count: int = 0
    gym_fitness_count: int = 0
    park_reserve_count: int = 0
    shopping_centre_count: int = 0
    medical_gp_count: int = 0
    supermarket_count: int = 0
    burleigh_drive_minutes: Optional[float] = None
    beach_access_minutes: Optional[float] = None
    travel_to_broadbeach_min: Optional[float] = None
    travel_to_airport_min: Optional[float] = None
    burleigh_access_score: Optional[float] = None
    beach_access_score: Optional[float] = None
    wellness_infrastructure_score: Optional[float] = None
    cafe_dining_score: Optional[float] = None
    outdoor_recreation_score: Optional[float] = None
    shopping_score: Optional[float] = None
    lifestyle_score: Optional[float] = None


class SchoolSummaryResponse(BaseModel):
    id: UUID
    name: str
    sector: str
    school_type: str
    address_suburb: str
    year_range: Optional[str] = None


class SuburbListItem(BaseModel):
    id: UUID
    name: str
    postcode: str
    tier: Optional[str] = None
    community_score: Optional[float] = None
    lifestyle_score: Optional[float] = None
    beach_access_minutes: Optional[float] = None

    @computed_field
    @property
    def slug(self) -> str:
        return self.name.lower().replace(" ", "-")

    @computed_field
    @property
    def tier_label(self) -> str:
        return {"A": "Premium", "B": "Good", "C": "Acceptable"}.get(self.tier or "", "Unknown")


class SuburbDetailResponse(BaseModel):
    id: UUID
    name: str
    postcode: str
    tier: Optional[str] = None
    latitude: float
    longitude: float
    lga: Optional[str] = None
    metrics: Optional[SuburbMetricResponse] = None
    lifestyle: Optional[SuburbLifestyleResponse] = None
    schools: list[SchoolSummaryResponse] = []

    @computed_field
    @property
    def slug(self) -> str:
        return self.name.lower().replace(" ", "-")

    @computed_field
    @property
    def tier_label(self) -> str:
        return {"A": "Premium", "B": "Good", "C": "Acceptable"}.get(self.tier or "", "Unknown")
