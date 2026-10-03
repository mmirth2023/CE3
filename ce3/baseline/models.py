from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class BaselineReference(BaseModel):
    """
    Canonical reference representation for established or expected
    system behavior at a defined point or period in time.

    A baseline is a reference against which observed system state
    and response can later be compared.

    It is not a prediction and does not determine future outcomes.

    The model preserves the reference state, its temporal validity,
    supporting observations, comparable historical states, and the
    conditions under which the baseline is considered applicable.
    """

    id: str

    system_id: str

    dimension: str

    established_at: datetime

    valid_from: datetime | None = None
    valid_to: datetime | None = None

    reference_state: dict[str, Any] = Field(
        default_factory=dict
    )

    reference_observation_ids: list[str] = Field(
        default_factory=list
    )

    comparable_state_ids: list[str] = Field(
        default_factory=list
    )

    conditions: dict[str, Any] = Field(
        default_factory=dict
    )

    stability: float = Field(
        ge=0.0,
        le=1.0,
    )

    confidence: float = Field(
        ge=0.0,
        le=1.0,
    )

    metadata: dict[str, Any] = Field(
        default_factory=dict
    )