from __future__ import annotations
from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, ConfigDict, HttpUrl


class PropertyIngestRequest(BaseModel):
    url: str


class PropertyFeatureResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    feature_key: str
    feature_value: str
    feature_type: str
    confidence: Optional[float]
    source: str


class PropertyImageResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    image_url: str
    image_order: int
    image_type: str
    caption: Optional[str]


class PropertyResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    family_id: UUID
    suburb_id: Optional[UUID]
    source_url: Optional[str]
    source_platform: Optional[str]
    address_street: str
    address_suburb: str
    address_state: str
    address_postcode: str
    property_type: str
    bedrooms: Optional[int]
    bathrooms: Optional[float]
    car_spaces: Optional[int]
    land_area_sqm: Optional[int]
    house_area_sqm: Optional[int]
    listing_price_aud: Optional[int]
    price_range_low_aud: Optional[int]
    price_range_high_aud: Optional[int]
    price_is_range: bool
    description_text: Optional[str]
    flood_risk_category: Optional[str]
    agent_name: Optional[str]
    agency_name: Optional[str]
    data_quality_score: int
    status: str
    is_favourite: bool
    family_notes: Optional[str]
    created_at: datetime
    auto_discovered: bool
    viewed_at: Optional[datetime]
    features: list[PropertyFeatureResponse] = []
    images: list[PropertyImageResponse] = []


class PropertyListResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    address_street: str
    address_suburb: str
    address_postcode: str
    property_type: str
    bedrooms: Optional[int]
    bathrooms: Optional[float]
    listing_price_aud: Optional[int]
    status: str
    is_favourite: bool
    created_at: datetime
    auto_discovered: bool
    viewed_at: Optional[datetime]


class PropertyIngestResponse(BaseModel):
    property_id: UUID
    status: str


class PropertyUpdateRequest(BaseModel):
    status: Optional[str] = None
    is_favourite: Optional[bool] = None
    family_notes: Optional[str] = None
