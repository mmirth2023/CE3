from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class ControlStatus(str, Enum):
    """
    Broad territorial/control status.

    This deliberately avoids pretending that territorial control
    can always be represented as a precise binary fact.
    """

    CONTROLLED = "controlled"
    CONTESTED = "contested"
    LOST = "lost"
    UNKNOWN = "unknown"


class ActivityLevel(str, Enum):
    """Qualitative level of military activity."""

    NONE = "none"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"
    UNKNOWN = "unknown"


class DiplomaticStatus(str, Enum):
    """Broad diplomatic condition."""

    NONE = "none"
    CONTACT = "contact"
    NEGOTIATION = "negotiation"
    AGREEMENT = "agreement"
    BREAKDOWN = "breakdown"
    UNKNOWN = "unknown"


class PoliticalStatus(str, Enum):
    """Broad political condition relevant to the conflict."""

    STABLE = "stable"
    CHANGING = "changing"
    DISRUPTED = "disrupted"
    UNKNOWN = "unknown"


class EconomicStatus(str, Enum):
    """Broad economic condition relevant to the conflict."""

    STABLE = "stable"
    PRESSURED = "pressured"
    DISRUPTED = "disrupted"
    CRITICAL = "critical"
    UNKNOWN = "unknown"


class HumanitarianStatus(str, Enum):
    """Broad humanitarian condition."""

    STABLE = "stable"
    STRAINED = "strained"
    SEVERE = "severe"
    CRITICAL = "critical"
    UNKNOWN = "unknown"


class TerritorialState(BaseModel):
    """
    State concerning a particular location or territorial entity.
    """

    entity: str

    status: ControlStatus = ControlStatus.UNKNOWN

    confidence: float = Field(
        ge=0.0,
        le=1.0,
    )

    source_event_ids: list[str] = Field(
        default_factory=list,
    )


class MilitaryState(BaseModel):
    """Current derived military activity state."""

    activity_level: ActivityLevel = ActivityLevel.UNKNOWN

    source_event_ids: list[str] = Field(
        default_factory=list,
    )


class ConflictState(BaseModel):
    """
    Derived state of a conflict at a specific point in time.

    ConflictState is derived state. It is not a replacement for
    the underlying Event history.
    """

    conflict_id: str

    as_of: datetime

    territorial: list[TerritorialState] = Field(
        default_factory=list,
    )

    military: MilitaryState = Field(
        default_factory=MilitaryState,
    )

    diplomatic: DiplomaticStatus = DiplomaticStatus.UNKNOWN

    political: PoliticalStatus = PoliticalStatus.UNKNOWN

    economic: EconomicStatus = EconomicStatus.UNKNOWN

    humanitarian: HumanitarianStatus = HumanitarianStatus.UNKNOWN

    source_event_ids: list[str] = Field(
        default_factory=list,
    )

    confidence: float = Field(
        ge=0.0,
        le=1.0,
    )

    uncertainty: list[str] = Field(
        default_factory=list,
    )

    metadata: dict[str, Any] = Field(
        default_factory=dict,
    )