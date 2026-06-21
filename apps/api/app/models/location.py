import uuid
from sqlalchemy import (
    Boolean, Column, CheckConstraint, DateTime, ForeignKey,
    Integer, Numeric, String, Text, UniqueConstraint, func,
)
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship

from app.models.base import Base, TimestampMixin


class Suburb(TimestampMixin, Base):
    __tablename__ = "suburbs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(Text, nullable=False, unique=True)
    postcode = Column(String(4), nullable=False)
    state = Column(String(3), nullable=False, default="QLD")
    lga = Column(Text, default="Gold Coast City Council")
    latitude = Column(Numeric(9, 6), nullable=False)
    longitude = Column(Numeric(9, 6), nullable=False)
    bounding_box = Column(JSONB)
    tier = Column(String(1))
    is_active = Column(Boolean, nullable=False, default=True)
    abs_sa2_code = Column(Text)
    police_division = Column(Text)

    __table_args__ = (
        CheckConstraint("tier IN ('A', 'B', 'C')", name="suburbs_tier_check"),
    )

    metrics = relationship("SuburbMetric", back_populates="suburb", uselist=False)
    lifestyle_assets = relationship("SuburbLifestyleAsset", back_populates="suburb", uselist=False)
    school_catchments = relationship("SchoolCatchment", back_populates="suburb")


class SuburbMetric(TimestampMixin, Base):
    __tablename__ = "suburb_metrics"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    suburb_id = Column(UUID(as_uuid=True), ForeignKey("suburbs.id"), nullable=False, unique=True)
    owner_occupier_rate = Column(Numeric(5, 2))
    owner_occupier_score = Column(Numeric(4, 2))
    family_density_pct = Column(Numeric(5, 2))
    family_density_score = Column(Numeric(4, 2))
    educational_attainment_pct = Column(Numeric(5, 2))
    educational_attainment_score = Column(Numeric(4, 2))
    median_weekly_household_income_aud = Column(Integer)
    median_income_score = Column(Numeric(4, 2))
    crime_index = Column(Numeric(6, 2))
    crime_score = Column(Numeric(4, 2))
    community_engagement_score = Column(Numeric(4, 2))
    community_score = Column(Numeric(4, 2))
    abs_data_year = Column(Integer, default=2021)
    crime_data_quarter = Column(Text)
    last_refreshed_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    suburb = relationship("Suburb", back_populates="metrics")


class SuburbLifestyleAsset(TimestampMixin, Base):
    __tablename__ = "suburb_lifestyle_assets"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    suburb_id = Column(UUID(as_uuid=True), ForeignKey("suburbs.id"), nullable=False, unique=True)
    cafe_restaurant_count = Column(Integer, default=0)
    gym_fitness_count = Column(Integer, default=0)
    pilates_yoga_count = Column(Integer, default=0)
    park_reserve_count = Column(Integer, default=0)
    shopping_centre_count = Column(Integer, default=0)
    medical_gp_count = Column(Integer, default=0)
    childcare_count = Column(Integer, default=0)
    supermarket_count = Column(Integer, default=0)
    burleigh_drive_minutes = Column(Numeric(5, 1))
    burleigh_access_score = Column(Numeric(4, 2))
    beach_access_minutes = Column(Numeric(5, 1))
    beach_access_score = Column(Numeric(4, 2))
    wellness_infrastructure_score = Column(Numeric(4, 2))
    cafe_dining_score = Column(Numeric(4, 2))
    outdoor_recreation_score = Column(Numeric(4, 2))
    shopping_score = Column(Numeric(4, 2))
    lifestyle_score = Column(Numeric(4, 2))
    travel_to_broadbeach_min = Column(Numeric(5, 1))
    travel_to_airport_min = Column(Numeric(5, 1))
    travel_to_robina_hospital_min = Column(Numeric(5, 1))
    osm_poi_counts = Column(JSONB)
    google_poi_counts = Column(JSONB)
    travel_times_fetched_at = Column(DateTime(timezone=True))
    poi_counts_fetched_at = Column(DateTime(timezone=True))
    last_refreshed_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    suburb = relationship("Suburb", back_populates="lifestyle_assets")


class LifestyleAssetCategory(Base):
    __tablename__ = "lifestyle_asset_categories"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    key = Column(Text, nullable=False, unique=True)
    label = Column(Text, nullable=False)
    icon = Column(Text)
    google_type = Column(Text)
    osm_tag = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class School(TimestampMixin, Base):
    __tablename__ = "schools"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(Text, nullable=False)
    school_type = Column(Text, nullable=False)
    sector = Column(Text, nullable=False)
    suburb_id = Column(UUID(as_uuid=True), ForeignKey("suburbs.id"))
    address_street = Column(Text)
    address_suburb = Column(Text, nullable=False)
    address_postcode = Column(String(4))
    latitude = Column(Numeric(9, 6))
    longitude = Column(Numeric(9, 6))
    acara_school_id = Column(Text, unique=True)
    year_range = Column(Text)
    total_enrolments = Column(Integer)
    icsea = Column(Integer)
    website_url = Column(Text)
    is_active = Column(Boolean, nullable=False, default=True)

    __table_args__ = (
        CheckConstraint("school_type IN ('primary', 'secondary', 'combined', 'special')", name="schools_type_check"),
        CheckConstraint("sector IN ('government', 'catholic', 'independent')", name="schools_sector_check"),
    )

    catchments = relationship("SchoolCatchment", back_populates="school")
    metrics = relationship("SchoolMetric", back_populates="school", uselist=False)


class SchoolCatchment(Base):
    __tablename__ = "school_catchments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    school_id = Column(UUID(as_uuid=True), ForeignKey("schools.id"), nullable=False)
    suburb_id = Column(UUID(as_uuid=True), ForeignKey("suburbs.id"), nullable=False)
    catchment_type = Column(Text, nullable=False, default="primary")
    is_guaranteed = Column(Boolean, nullable=False, default=True)
    notes = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    __table_args__ = (
        UniqueConstraint("school_id", "suburb_id", "catchment_type", name="school_catchments_unique"),
        CheckConstraint("catchment_type IN ('primary', 'secondary', 'out_of_catchment_accepted')", name="school_catchments_type_check"),
    )

    school = relationship("School", back_populates="catchments")
    suburb = relationship("Suburb", back_populates="school_catchments")


class SchoolMetric(TimestampMixin, Base):
    __tablename__ = "school_metrics"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    school_id = Column(UUID(as_uuid=True), ForeignKey("schools.id"), nullable=False, unique=True)
    naplan_reading_pct_above_nms = Column(Numeric(5, 2))
    naplan_numeracy_pct_above_nms = Column(Numeric(5, 2))
    naplan_writing_pct_above_nms = Column(Numeric(5, 2))
    naplan_data_year = Column(Integer)
    wellbeing_score = Column(Numeric(4, 2))
    parent_community_score = Column(Numeric(4, 2))
    academic_outcomes_score = Column(Numeric(4, 2))
    commute_score = Column(Numeric(4, 2))
    extracurricular_score = Column(Numeric(4, 2))
    pathway_score = Column(Numeric(4, 2))
    school_score = Column(Numeric(4, 2))
    attendance_rate_pct = Column(Numeric(5, 2))
    staff_to_student_ratio = Column(Numeric(5, 2))
    annual_fee_aud = Column(Integer)
    has_boarding = Column(Boolean, default=False)
    extracurricular_notes = Column(Text)
    data_year = Column(Integer)
    last_refreshed_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    school = relationship("School", back_populates="metrics")
