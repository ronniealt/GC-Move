import uuid
from sqlalchemy import (
    Boolean, Column, CheckConstraint, Date, DateTime, ForeignKey,
    Integer, Numeric, Text, Time, UniqueConstraint, func,
)
from sqlalchemy.dialects.postgresql import ARRAY, INET, UUID, JSONB
from sqlalchemy.orm import relationship

from app.models.base import Base, TimestampMixin


class Inspection(TimestampMixin, Base):
    __tablename__ = "inspections"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    family_id = Column(UUID(as_uuid=True), ForeignKey("families.id"), nullable=False)
    property_id = Column(UUID(as_uuid=True), ForeignKey("properties.id", ondelete="CASCADE"), nullable=False)
    inspection_type = Column(Text, nullable=False, default="open_home")
    scheduled_at = Column(DateTime(timezone=True))
    completed_at = Column(DateTime(timezone=True))
    status = Column(Text, nullable=False, default="scheduled")
    overall_impression = Column(Text)
    notes = Column(Text)
    street_feel = Column(Text)
    neighbour_observations = Column(Text)
    deal_breakers_found = Column(ARRAY(Text))
    report_url = Column(Text)
    report_summary = Column(Text)
    pest_issues = Column(Boolean)
    structural_issues = Column(Boolean)

    __table_args__ = (
        CheckConstraint("inspection_type IN ('open_home', 'private', 'building_pest', 'virtual')", name="inspections_type_check"),
        CheckConstraint("status IN ('scheduled', 'completed', 'cancelled', 'missed')", name="inspections_status_check"),
        CheckConstraint("overall_impression IN ('love', 'like', 'neutral', 'dislike', 'reject')", name="inspections_impression_check"),
    )

    property = relationship("Property")


class AIAdvisorThread(TimestampMixin, Base):
    __tablename__ = "ai_advisor_threads"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    family_id = Column(UUID(as_uuid=True), ForeignKey("families.id"), nullable=False)
    openai_thread_id = Column(Text, nullable=False, unique=True)
    thread_name = Column(Text)
    is_active = Column(Boolean, nullable=False, default=True)
    message_count = Column(Integer, nullable=False, default=0)
    last_message_at = Column(DateTime(timezone=True))

    messages = relationship("AIAdvisorMessage", back_populates="thread", cascade="all, delete-orphan")


class AIAdvisorMessage(Base):
    __tablename__ = "ai_advisor_messages"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    family_id = Column(UUID(as_uuid=True), ForeignKey("families.id"), nullable=False)
    thread_id = Column(UUID(as_uuid=True), ForeignKey("ai_advisor_threads.id", ondelete="CASCADE"), nullable=False)
    role = Column(Text, nullable=False)
    content = Column(Text, nullable=False)
    openai_message_id = Column(Text)
    property_id = Column(UUID(as_uuid=True), ForeignKey("properties.id"))
    tokens_used = Column(Integer)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    __table_args__ = (
        CheckConstraint("role IN ('user', 'assistant', 'system')", name="ai_advisor_messages_role_check"),
    )

    thread = relationship("AIAdvisorThread", back_populates="messages")


class NotificationSettings(TimestampMixin, Base):
    __tablename__ = "notification_settings"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    family_id = Column(UUID(as_uuid=True), ForeignKey("families.id"), nullable=False, unique=True)
    email_new_evaluation = Column(Boolean, nullable=False, default=True)
    email_rank_change = Column(Boolean, nullable=False, default=True)
    email_daily_digest = Column(Boolean, nullable=False, default=False)
    email_inspection_reminder = Column(Boolean, nullable=False, default=True)
    push_enabled = Column(Boolean, nullable=False, default=False)
    digest_time = Column(Time, default="07:00:00")


class MarketSnapshot(Base):
    __tablename__ = "market_snapshots"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    suburb_id = Column(UUID(as_uuid=True), ForeignKey("suburbs.id"), nullable=False)
    snapshot_date = Column(Date, nullable=False)
    median_house_price_aud = Column(Integer)
    median_unit_price_aud = Column(Integer)
    days_on_market_median = Column(Integer)
    clearance_rate_pct = Column(Numeric(5, 2))
    price_growth_1yr_pct = Column(Numeric(6, 2))
    price_growth_3yr_pct = Column(Numeric(6, 2))
    price_growth_5yr_pct = Column(Numeric(6, 2))
    rental_yield_pct = Column(Numeric(5, 2))
    supply_demand_index = Column(Numeric(5, 2))
    source = Column(Text, default="manual")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    __table_args__ = (
        UniqueConstraint("suburb_id", "snapshot_date", "source", name="market_snapshots_unique"),
        CheckConstraint("source IN ('manual', 'proptrack', 'reiq', 'corelogic')", name="market_snapshots_source_check"),
    )


class AuditLog(Base):
    __tablename__ = "audit_log"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    family_id = Column(UUID(as_uuid=True), ForeignKey("families.id"))
    member_id = Column(UUID(as_uuid=True), ForeignKey("family_members.id"))
    actor_type = Column(Text, nullable=False)
    action = Column(Text, nullable=False)
    entity_type = Column(Text)
    entity_id = Column(UUID(as_uuid=True))
    old_state = Column(JSONB)
    new_state = Column(JSONB)
    ip_address = Column(INET)
    user_agent = Column(Text)
    session_id = Column(Text)
    notes = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    __table_args__ = (
        CheckConstraint("actor_type IN ('user', 'system', 'ai', 'admin')", name="audit_log_actor_type_check"),
    )
