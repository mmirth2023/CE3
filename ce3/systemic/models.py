from __future__ import annotations

from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field

from ce3.change.models import StateChangeAssessment


class SystemicLevel(str, Enum):
    NONE = "none"
    LOCAL = "local"
    SYSTEMIC = "systemic"


class SystemicChangeAssessment(BaseModel):
    """
    Assessment of whether a material state change has
    sufficient structural breadth or cross-system relevance
    to be considered systemic.

    This model does not establish propagation, causality,
    regime transition, economic impact, or future outcomes.
    """

    id: str

    assessed_at: datetime

    state_change: StateChangeAssessment

    level: SystemicLevel

    scope: float = Field(
        ge=0.0,
        le=1.0,
    )

    dependency_relevance: float = Field(
        ge=0.0,
        le=1.0,
    )

    cross_domain_relevance: float = Field(
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

    @property
    def is_systemic(self) -> bool:
        return self.level == SystemicLevel.SYSTEMIC