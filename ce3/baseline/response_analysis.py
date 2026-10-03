from __future__ import annotations

from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class ResponseClassification(str, Enum):
    """
    Descriptive classification of an observed response
    relative to an established deviation.
    """

    NORMALIZED = "normalized"
    AMPLIFIED = "amplified"
    PERSISTENT = "persistent"
    REVERSAL = "reversal"
    STABLE = "stable"
    MIXED = "mixed"
    UNKNOWN = "unknown"


class ResponseAnalysis(BaseModel):
    """
    Canonical representation of an analyzed system response.

    The analysis describes the observed relationship between
    a baseline deviation and subsequent system response.

    It does not determine causality, propagation, regime transition,
    economic consequences, or future outcomes.
    """

    id: str

    deviation_id: str

    response_id: str

    system_id: str

    dimension: str

    classification: ResponseClassification = (
        ResponseClassification.UNKNOWN
    )

    baseline_distance_before: float = Field(
        default=0.0,
        ge=0.0,
    )

    baseline_distance_after: float = Field(
        default=0.0,
        ge=0.0,
    )

    response_strength: float = Field(
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

    affected_paths: list[str] = Field(
        default_factory=list
    )

    source_event_ids: list[str] = Field(
        default_factory=list
    )

    source_observation_ids: list[str] = Field(
        default_factory=list
    )

    metadata: dict[str, Any] = Field(
        default_factory=dict
    )