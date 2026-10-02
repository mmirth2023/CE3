from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class StateVersion(BaseModel):
    """
    Immutable logical snapshot of CE³'s canonical system state.

    A StateVersion records what the engine believed the state to be
    at a particular state time. It does not itself determine how the
    state was derived.
    """

    id: str

    state_time: datetime

    state: dict[str, Any] = Field(
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

    metadata: dict[str, Any] = Field(
        default_factory=dict,
    )