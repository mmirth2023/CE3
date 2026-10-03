from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field

from ce3.materiality.models import MaterialityAssessment
from ce3.temporal.state_diff import StateDiff


class StateChangeAssessment(BaseModel):
    """
    Integrated assessment of a structural change between two
    canonical CE³ state versions.

    This model connects state difference with materiality while
    preserving the underlying evidence trail.

    It does not determine causality, propagation, economic impact,
    or future outcomes.
    """

    id: str

    assessed_at: datetime

    state_diff: StateDiff

    materiality: MaterialityAssessment

    affected_paths: list[str] = Field(
        default_factory=list,
    )

    source_event_ids: list[str] = Field(
        default_factory=list,
    )

    source_observation_ids: list[str] = Field(
        default_factory=list,
    )

    metadata: dict[str, Any] = Field(
        default_factory=dict,
    )

    @property
    def is_material(self) -> bool:
        """
        Whether the underlying state difference was assessed
        as materially significant.
        """

        return self.materiality.level.value not in {
            "none",
            "low",
        }