from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class ResponseDirection(str, Enum):
    """
    Direction of observed system response.
    """

    INCREASE = "increase"
    DECREASE = "decrease"
    MIXED = "mixed"
    NONE = "none"


class SystemResponse(BaseModel):
    """
    Canonical representation of an observed system response
    following a detected state change or baseline deviation.

    This is a descriptive response object.

    It does not determine causality, propagation, regime transition,
    economic consequences, or future outcomes.
    """

    id: str

    system_id: str

    dimension: str

    deviation_id: str

    observed_at: datetime

    response_state_before: dict[str, Any] = Field(
        default_factory=dict
    )

    response_state_after: dict[str, Any] = Field(
        default_factory=dict
    )

    affected_paths: list[str] = Field(
        default_factory=list
    )

    direction: ResponseDirection = ResponseDirection.NONE

    magnitude: float = Field(
        default=0.0,
        ge=0.0,
    )

    latency_seconds: float = Field(
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