from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class DeviationDirection(str, Enum):
    """
    Direction of observed deviation relative to a baseline.
    """

    BELOW = "below"
    ABOVE = "above"
    MIXED = "mixed"
    NONE = "none"


class BaselineDeviation(BaseModel):
    """
    Canonical representation of observed system deviation
    relative to an established baseline.

    This is a descriptive comparison object.

    It does not determine causality, materiality, propagation,
    regime transition, economic consequences, or future outcomes.
    """

    id: str

    baseline_id: str

    system_id: str

    dimension: str

    observed_at: datetime

    baseline_state: dict[str, Any] = Field(
        default_factory=dict
    )

    observed_state: dict[str, Any] = Field(
        default_factory=dict
    )

    affected_paths: list[str] = Field(
        default_factory=list
    )

    direction: DeviationDirection = DeviationDirection.NONE

    magnitude: float = Field(
        default=0.0,
        ge=0.0,
    )

    persistence: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
    )

    confidence: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
    )

    rationale: str = ""

    source_event_ids: list[str] = Field(
        default_factory=list
    )

    source_observation_ids: list[str] = Field(
        default_factory=list
    )

    metadata: dict[str, Any] = Field(
        default_factory=dict
    )