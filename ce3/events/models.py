from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class EventType(str, Enum):
    """
    Canonical event categories recognized by CE³.

    These are deliberately broad at this stage.
    More specific event taxonomies can be added later.
    """

    MILITARY_ACTION = "military_action"
    FACILITY_DAMAGE = "facility_damage"
    TERRITORY_CHANGE = "territory_change"

    DIPLOMATIC_ACTION = "diplomatic_action"
    AGREEMENT = "agreement"
    NEGOTIATION = "negotiation"

    POLITICAL_CHANGE = "political_change"
    LEADERSHIP_CHANGE = "leadership_change"
    POLICY_CHANGE = "policy_change"

    ECONOMIC_SHOCK = "economic_shock"
    SANCTION = "sanction"
    TRADE_CHANGE = "trade_change"

    INFRASTRUCTURE_CHANGE = "infrastructure_change"

    HUMANITARIAN_EVENT = "humanitarian_event"

    INFORMATION_EVENT = "information_event"

    OTHER = "other"


class EventSeverity(str, Enum):
    """Qualitative magnitude of an event."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"
    UNKNOWN = "unknown"


class Event(BaseModel):
    """
    Normalized representation of an event in the conflict.

    An Event is distinct from a Claim:
    a Claim is an assertion supported or contradicted by evidence;
    an Event is CE³'s normalized representation of something that
    occurred or is assessed to have occurred.
    """

    id: str

    conflict_id: str

    event_type: EventType

    occurred_at: datetime

    detected_at: datetime

    title: str

    description: str

    severity: EventSeverity = EventSeverity.UNKNOWN

    location: str | None = None

    actors: list[str] = Field(default_factory=list)

    affected_entities: list[str] = Field(default_factory=list)

    claim_ids: list[str] = Field(default_factory=list)

    confidence: float = Field(
        ge=0.0,
        le=1.0,
    )

    metadata: dict[str, Any] = Field(default_factory=dict)