import uuid
from sqlalchemy import (
    Boolean, Column, CheckConstraint, Date, DateTime, ForeignKey,
    Integer, Numeric, String, Text, func,
)
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship

from app.models.base import Base, TimestampMixin


class Family(TimestampMixin, Base):
    __tablename__ = "families"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    display_name = Column(Text, nullable=False)
    primary_suburb_target = Column(Text)
    budget_min_aud = Column(Integer)
    budget_max_aud = Column(Integer)
    target_move_date = Column(Date)
    is_active = Column(Boolean, nullable=False, default=True)
    onboarding_completed = Column(Boolean, nullable=False, default=False)
    scoring_model_version = Column(Text, nullable=False, default="v1")
    weight_community = Column(Numeric(4, 3), nullable=False, default=0.250)
    weight_lifestyle = Column(Numeric(4, 3), nullable=False, default=0.200)
    weight_school = Column(Numeric(4, 3), nullable=False, default=0.200)
    weight_property = Column(Numeric(4, 3), nullable=False, default=0.200)
    weight_financial = Column(Numeric(4, 3), nullable=False, default=0.150)

    __table_args__ = (
        CheckConstraint(
            "ABS((weight_community + weight_lifestyle + weight_school + weight_property + weight_financial) - 1.0) < 0.001",
            name="weights_sum_to_one",
        ),
    )

    members = relationship("FamilyMember", back_populates="family", foreign_keys="FamilyMember.family_id")
    users = relationship("FamilyUser", back_populates="family")
    invites = relationship("FamilyInvite", back_populates="family")
    preferences = relationship("FamilyPreference", back_populates="family")
    memory = relationship("FamilyMemory", back_populates="family")


class FamilyUser(TimestampMixin, Base):
    __tablename__ = "family_users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    family_id = Column(UUID(as_uuid=True), ForeignKey("families.id", ondelete="RESTRICT"), nullable=False)
    clerk_user_id = Column(Text, nullable=False, unique=True)
    family_member_id = Column(UUID(as_uuid=True), ForeignKey("family_members.id", ondelete="SET NULL"))
    role = Column(Text, nullable=False, default="member")
    display_name = Column(Text, nullable=False)
    email = Column(Text, nullable=False)

    __table_args__ = (
        CheckConstraint("role IN ('primary', 'member')", name="family_users_role_check"),
    )

    family = relationship("Family", back_populates="users")
    family_member = relationship("FamilyMember", foreign_keys=[family_member_id])


class FamilyInvite(Base):
    __tablename__ = "family_invites"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    family_id = Column(UUID(as_uuid=True), ForeignKey("families.id", ondelete="CASCADE"), nullable=False)
    invited_by_user_id = Column(UUID(as_uuid=True), ForeignKey("family_users.id", ondelete="CASCADE"), nullable=False)
    email = Column(Text, nullable=False)
    role = Column(Text, nullable=False, default="member")
    invite_token = Column(Text, nullable=False, unique=True)
    status = Column(Text, nullable=False, default="pending")
    expires_at = Column(DateTime(timezone=True), nullable=False)
    accepted_at = Column(DateTime(timezone=True))
    accepted_by_user_id = Column(UUID(as_uuid=True), ForeignKey("family_users.id", ondelete="SET NULL"))
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    __table_args__ = (
        CheckConstraint("role IN ('primary', 'member')", name="family_invites_role_check"),
        CheckConstraint("status IN ('pending', 'accepted', 'expired', 'revoked')", name="family_invites_status_check"),
    )

    family = relationship("Family", back_populates="invites")


class FamilyMember(TimestampMixin, Base):
    __tablename__ = "family_members"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    family_id = Column(UUID(as_uuid=True), ForeignKey("families.id", ondelete="RESTRICT"), nullable=False)
    first_name = Column(Text, nullable=False)
    role = Column(Text, nullable=False)
    age = Column(Integer)
    birth_year = Column(Integer)
    notes = Column(Text)
    avatar_emoji = Column(Text, default="👤")

    __table_args__ = (
        CheckConstraint("role IN ('primary_adult', 'secondary_adult', 'child', 'pet')", name="family_members_role_check"),
        CheckConstraint("age >= 0 AND age <= 120", name="family_members_age_check"),
    )

    family = relationship("Family", back_populates="members", foreign_keys=[family_id])


class FamilyPreference(TimestampMixin, Base):
    __tablename__ = "family_preferences"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    family_id = Column(UUID(as_uuid=True), ForeignKey("families.id", ondelete="RESTRICT"), nullable=False)
    attribute = Column(Text, nullable=False)
    category = Column(Text, nullable=False)
    current_weight = Column(Numeric(3, 1), nullable=False, default=2.5)
    confidence = Column(Numeric(3, 2), nullable=False, default=0.0)
    status = Column(Text, nullable=False, default="Emerging")
    positive_signal_count = Column(Integer, nullable=False, default=0)
    negative_signal_count = Column(Integer, nullable=False, default=0)
    last_signal_at = Column(DateTime(timezone=True))
    is_deal_breaker = Column(Boolean, nullable=False, default=False)
    deal_breaker_set_at = Column(DateTime(timezone=True))
    notes = Column(Text)

    __table_args__ = (
        CheckConstraint("status IN ('Emerging', 'Confirmed', 'Contradicted', 'Retired', 'Manual')", name="family_preferences_status_check"),
    )

    family = relationship("Family", back_populates="preferences")


class FamilyMemory(TimestampMixin, Base):
    __tablename__ = "family_memory"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    family_id = Column(UUID(as_uuid=True), ForeignKey("families.id", ondelete="RESTRICT"), nullable=False)
    member_id = Column(UUID(as_uuid=True), ForeignKey("family_members.id"))
    memory_type = Column(Text, nullable=False)
    attribute = Column(Text)
    content = Column(Text, nullable=False)
    structured = Column(JSONB)
    source = Column(Text)
    confidence = Column(Numeric(3, 2), nullable=False, default=1.0)
    expires_at = Column(DateTime(timezone=True))

    __table_args__ = (
        CheckConstraint("memory_type IN ('Permanent', 'Preference', 'Learned', 'Session', 'Decision')", name="family_memory_type_check"),
    )

    family = relationship("Family", back_populates="memory")
    member = relationship("FamilyMember", foreign_keys=[member_id])


class MemoryEvent(Base):
    __tablename__ = "memory_events"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    family_id = Column(UUID(as_uuid=True), ForeignKey("families.id", ondelete="RESTRICT"), nullable=False)
    memory_id = Column(UUID(as_uuid=True), ForeignKey("family_memory.id"))
    preference_id = Column(UUID(as_uuid=True), ForeignKey("family_preferences.id"))
    event_type = Column(Text, nullable=False)
    attribute = Column(Text)
    old_value = Column(JSONB)
    new_value = Column(JSONB)
    triggered_by = Column(Text)
    notes = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
