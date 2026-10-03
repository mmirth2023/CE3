from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class GlobalSystemState(BaseModel):
    """
    Canonical generalized representation of CE³ system state.

    This model represents the observable configuration of a
    system at a point in time.

    It is intentionally domain-agnostic. Conflict-specific,
    economic, financial, political, infrastructure, market,
    and other domain states can be represented through the
    corresponding dimensions.

    The model describes state. It does not determine causality,
    propagation, future outcomes, or economic consequences.
    """

    id: str

    state_time: datetime

    entities: dict[str, Any] = Field(
        default_factory=dict,
    )

    relationships: dict[str, Any] = Field(
        default_factory=dict,
    )

    physical: dict[str, Any] = Field(
        default_factory=dict,
    )

    economic: dict[str, Any] = Field(
        default_factory=dict,
    )

    financial: dict[str, Any] = Field(
        default_factory=dict,
    )

    political: dict[str, Any] = Field(
        default_factory=dict,
    )

    information: dict[str, Any] = Field(
        default_factory=dict,
    )

    infrastructure: dict[str, Any] = Field(
        default_factory=dict,
    )

    market: dict[str, Any] = Field(
        default_factory=dict,
    )

    constraints: dict[str, Any] = Field(
        default_factory=dict,
    )

    dependencies: dict[str, Any] = Field(
        default_factory=dict,
    )

    active_shocks: dict[str, Any] = Field(
        default_factory=dict,
    )

    observability: dict[str, Any] = Field(
        default_factory=dict,
    )

    adaptations: dict[str, Any] = Field(
        default_factory=dict,
    )

    propagation_paths: dict[str, Any] = Field(
        default_factory=dict,
    )

    source_event_ids: list[str] = Field(
        default_factory=list,
    )

    source_observation_ids: list[str] = Field(
        default_factory=list,
    )

    confidence: float = Field(
        ge=0.0,
        le=1.0,
    )

    uncertainty: dict[str, Any] = Field(
        default_factory=dict,
    )

    metadata: dict[str, Any] = Field(
        default_factory=dict,
    )