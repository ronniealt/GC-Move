import uuid
from sqlalchemy import (
    Boolean, Column, CheckConstraint, DateTime, ForeignKey,
    Integer, Numeric, String, Text, func,
)
from sqlalchemy.dialects.postgresql import UUID, TSVECTOR
from sqlalchemy.orm import relationship

from app.models.base import Base, TimestampMixin


class Property(TimestampMixin, Base):
    __tablename__ = "properties"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    family_id = Column(UUID(as_uuid=True), ForeignKey("families.id", ondelete="RESTRICT"), nullable=False)
    suburb_id = Column(UUID(as_uuid=True), ForeignKey("suburbs.id"))
    source_url = Column(Text)
    source_platform = Column(Text)
    source_listing_id = Column(Text)
    address_street = Column(Text, nullable=False)
    address_suburb = Column(Text, nullable=False)
    address_state = Column(Text, nullable=False, default="QLD")
    address_postcode = Column(String(4), nullable=False)
    latitude = Column(Numeric(9, 6))
    longitude = Column(Numeric(9, 6))
    property_type = Column(Text, nullable=False)
    bedrooms = Column(Integer)
    bathrooms = Column(Numeric(3, 1))
    car_spaces = Column(Integer)
    land_area_sqm = Column(Integer)
    house_area_sqm = Column(Integer)
    listing_price_aud = Column(Integer)
    price_range_low_aud = Column(Integer)
    price_range_high_aud = Column(Integer)
    price_is_range = Column(Boolean, nullable=False, default=False)
    description_text = Column(Text)
    # description_tsvector is GENERATED ALWAYS AS in DB; mapped read-only
    description_tsvector = Column(TSVECTOR)
    flood_risk_category = Column(Text, default="unknown")
    flood_risk_source_date = Column(DateTime(timezone=True))
    agent_name = Column(Text)
    agency_name = Column(Text)
    data_quality_score = Column(Integer, nullable=False, default=50)
    extraction_confidence = Column(Numeric(3, 2))
    status = Column(Text, nullable=False, default="saved")
    is_favourite = Column(Boolean, nullable=False, default=False)
    family_notes = Column(Text)

    __table_args__ = (
        CheckConstraint("property_type IN ('house', 'townhouse', 'unit', 'acreage', 'other')", name="properties_type_check"),
        CheckConstraint("status IN ('saved', 'shortlisted', 'inspecting', 'offer', 'rejected', 'sold', 'withdrawn')", name="properties_status_check"),
        CheckConstraint("flood_risk_category IN ('high', 'medium', 'low', 'none', 'unknown')", name="properties_flood_risk_check"),
        CheckConstraint("source_platform IN ('realestate', 'domain', 'manual', 'agent')", name="properties_platform_check"),
    )

    family = relationship("Family")
    suburb = relationship("Suburb")
    features = relationship("PropertyFeature", back_populates="property", cascade="all, delete-orphan")
    images = relationship("PropertyImage", back_populates="property", cascade="all, delete-orphan", order_by="PropertyImage.image_order")
    history = relationship("PropertyHistory", back_populates="property", cascade="all, delete-orphan")


class PropertyFeature(TimestampMixin, Base):
    __tablename__ = "property_features"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    family_id = Column(UUID(as_uuid=True), ForeignKey("families.id"), nullable=False)
    property_id = Column(UUID(as_uuid=True), ForeignKey("properties.id", ondelete="CASCADE"), nullable=False)
    feature_key = Column(Text, nullable=False)
    feature_value = Column(Text, nullable=False)
    feature_type = Column(Text, nullable=False, default="boolean")
    confidence = Column(Numeric(3, 2), default=1.0)
    source = Column(Text, default="extracted")

    __table_args__ = (
        CheckConstraint("feature_type IN ('boolean', 'text', 'numeric', 'enum')", name="property_features_type_check"),
        CheckConstraint("source IN ('extracted', 'manual', 'inferred')", name="property_features_source_check"),
    )

    property = relationship("Property", back_populates="features")


class PropertyImage(Base):
    __tablename__ = "property_images"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    family_id = Column(UUID(as_uuid=True), ForeignKey("families.id"), nullable=False)
    property_id = Column(UUID(as_uuid=True), ForeignKey("properties.id", ondelete="CASCADE"), nullable=False)
    image_url = Column(Text, nullable=False)
    image_order = Column(Integer, nullable=False, default=0)
    image_type = Column(Text, default="listing")
    caption = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    __table_args__ = (
        CheckConstraint("image_type IN ('listing', 'floorplan', 'streetview', 'inspection')", name="property_images_type_check"),
    )

    property = relationship("Property", back_populates="images")


class PropertyHistory(Base):
    __tablename__ = "property_history"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    family_id = Column(UUID(as_uuid=True), ForeignKey("families.id"), nullable=False)
    property_id = Column(UUID(as_uuid=True), ForeignKey("properties.id", ondelete="CASCADE"), nullable=False)
    event_type = Column(Text, nullable=False)
    old_value = Column(Text)
    new_value = Column(Text)
    event_date = Column(DateTime(timezone=True))
    notes = Column(Text)
    source = Column(Text, default="system")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    __table_args__ = (
        CheckConstraint(
            "event_type IN ('status_change', 'price_change', 'listed', 'relisted', 'price_drop', 'sold', 'withdrawn', 'passed_in')",
            name="property_history_event_type_check",
        ),
    )

    property = relationship("Property", back_populates="history")
