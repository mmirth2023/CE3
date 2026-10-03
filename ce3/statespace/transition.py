from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field

from .diff import StateSpaceDiff


class StateSpaceTransitionType(str, Enum):
    NONE = "none"
    NORMALIZATION = "normalization"
    DETERIORATION = "deterioration"
    RECOVERY = "recovery"
    STRUCTURAL_SHIFT = "structural_shift"
    DIMENSIONAL_SHIFT = "dimensional_shift"
    UNKNOWN = "unknown"


class StateSpaceTransition(BaseModel):
    """
    Describes an observed transition between two state-space
    positions.

    This model is descriptive rather than predictive. It records
    what changed between two observed positions and classifies the
    observed movement without asserting causality or forecasting
    what happens next.
    """

    id: str
    assessed_at: datetime

    previous_position_id: str
    current_position_id: str

    previous_state_time: datetime
    current_state_time: datetime

    transition_type: StateSpaceTransitionType

    changed_dimensions: list[str] = Field(
        default_factory=list
    )

    magnitude: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
    )

    confidence: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
    )

    state_space_diff: StateSpaceDiff

    rationale: list[str] = Field(
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

    @property
    def has_transition(self) -> bool:
        """
        Return True when the observed positions differ.
        """
        return self.transition_type != (
            StateSpaceTransitionType.NONE
        )

    @property
    def is_structural(self) -> bool:
        """
        Return True when the transition is classified as a
        structural shift.
        """
        return self.transition_type == (
            StateSpaceTransitionType.STRUCTURAL_SHIFT
        )