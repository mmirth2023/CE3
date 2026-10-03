from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field

from .transition import (
    StateSpaceTransition,
    StateSpaceTransitionType,
)


class StateSpaceTransitionSequence(BaseModel):
    """
    Describes an observed ordered sequence of state-space
    transitions.

    The sequence is descriptive. It records observed movement
    through state-space without forecasting future states,
    inferring causality, or assigning a probability to what
    happens next.
    """

    id: str

    start_time: datetime
    end_time: datetime

    transition_ids: list[str] = Field(
        default_factory=list
    )

    transition_types: list[
        StateSpaceTransitionType
    ] = Field(
        default_factory=list
    )

    changed_dimensions: list[str] = Field(
        default_factory=list
    )

    start_position_id: str | None = None
    end_position_id: str | None = None

    transition_count: int = Field(
        default=0,
        ge=0,
    )

    cumulative_magnitude: float = Field(
        default=0.0,
        ge=0.0,
    )

    average_confidence: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
    )

    has_structural_shift: bool = False

    rationale: list[str] = Field(
        default_factory=list
    )

    metadata: dict[str, Any] = Field(
        default_factory=dict
    )

    @property
    def is_empty(self) -> bool:
        """
        Return True when the sequence contains no transitions.
        """
        return self.transition_count == 0

    @property
    def transition_type_names(self) -> list[str]:
        """
        Return transition type values in sequence order.
        """
        return [
            transition_type.value
            for transition_type
            in self.transition_types
        ]