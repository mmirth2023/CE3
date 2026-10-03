from __future__ import annotations

from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class StateSpaceSequenceClassification(str, Enum):
    """
    Descriptive classification of an observed state-space sequence.
    """

    EMPTY = "empty"
    STABLE = "stable"
    DETERIORATING = "deteriorating"
    RECOVERING = "recovering"
    MIXED = "mixed"
    STRUCTURAL = "structural"
    REVERSAL = "reversal"
    COMPLEX = "complex"
    UNKNOWN = "unknown"


class StateSpaceSequenceAnalysis(BaseModel):
    """
    Describes observed characteristics of a state-space
    transition sequence.

    The analysis is descriptive. It does not forecast future
    states, infer causality, estimate probabilities, or determine
    which trajectory will occur next.
    """

    id: str

    sequence_id: str

    classification: StateSpaceSequenceClassification

    transition_count: int = Field(
        default=0,
        ge=0,
    )

    deterioration_count: int = Field(
        default=0,
        ge=0,
    )

    recovery_count: int = Field(
        default=0,
        ge=0,
    )

    normalization_count: int = Field(
        default=0,
        ge=0,
    )

    dimensional_shift_count: int = Field(
        default=0,
        ge=0,
    )

    structural_shift_count: int = Field(
        default=0,
        ge=0,
    )

    none_count: int = Field(
        default=0,
        ge=0,
    )

    unknown_count: int = Field(
        default=0,
        ge=0,
    )

    changed_dimensions: list[str] = Field(
        default_factory=list
    )

    repeated_dimensions: list[str] = Field(
        default_factory=list
    )

    reversal_detected: bool = False

    structural_shift_detected: bool = False

    dominant_transition_type: str | None = None

    dominant_dimension: str | None = None

    transition_density: float = Field(
        default=0.0,
        ge=0.0,
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

    rationale: list[str] = Field(
        default_factory=list
    )

    metadata: dict[str, Any] = Field(
        default_factory=dict
    )

    @property
    def is_structural(self) -> bool:
        """
        Return True when the observed sequence contains a
        structural shift.
        """
        return self.structural_shift_detected

    @property
    def is_reversal(self) -> bool:
        """
        Return True when the observed sequence contains a
        directional reversal.
        """
        return self.reversal_detected

    @property
    def has_repeated_dimensions(self) -> bool:
        """
        Return True when at least one dimension changed more than
        once within the sequence.
        """
        return bool(self.repeated_dimensions)