from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, Field


class MaterialityLevel(str, Enum):
    """
    Structural significance assigned to a state change.

    This is an assessment category, not a prediction and not
    a financial recommendation.
    """

    NONE = "none"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class MaterialityAssessment(BaseModel):
    """
    Explainable assessment of the significance of a state change.

    The component scores are deliberately kept separate so that
    later CE³ versions can improve the methodology without changing
    the underlying state-difference model.
    """

    level: MaterialityLevel

    magnitude: float = Field(
        ge=0.0,
        le=1.0,
    )

    structural_relevance: float = Field(
        ge=0.0,
        le=1.0,
    )

    persistence: float = Field(
        ge=0.0,
        le=1.0,
    )

    confidence: float = Field(
        ge=0.0,
        le=1.0,
    )

    rationale: list[str] = Field(
        default_factory=list,
    )