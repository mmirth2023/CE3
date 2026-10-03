from __future__ import annotations

from datetime import datetime

from ce3.materiality.engine import MaterialityEngine
from ce3.temporal.state_diff import StateDiff
from ce3.temporal.state_version import StateVersion

from .models import StateChangeAssessment


class StateChangeEngine:
    """
    Integrates canonical state versions, structural state
    differences, and materiality assessment.

    The engine does not determine causality, propagation,
    economic impact, or future outcomes.
    """

    def __init__(
        self,
        materiality_engine: MaterialityEngine | None = None,
    ) -> None:
        self.materiality_engine = (
            materiality_engine
            or MaterialityEngine()
        )

    def detect(
        self,
        *,
        change_id: str,
        previous: StateVersion,
        current: StateVersion,
        assessed_at: datetime,
        magnitude: float,
        structural_relevance: float,
        persistence: float,
        confidence: float,
        source_event_ids: list[str] | None = None,
        source_observation_ids: list[str] | None = None,
    ) -> StateChangeAssessment:
        """
        Compare two canonical state versions and produce an
        integrated state change assessment.
        """

        diff = StateDiff.between(
            previous,
            current,
        )

        return self.assess(
            change_id=change_id,
            diff=diff,
            assessed_at=assessed_at,
            magnitude=magnitude,
            structural_relevance=structural_relevance,
            persistence=persistence,
            confidence=confidence,
            source_event_ids=source_event_ids,
            source_observation_ids=source_observation_ids,
        )

    def assess(
        self,
        *,
        change_id: str,
        diff: StateDiff,
        assessed_at: datetime,
        magnitude: float,
        structural_relevance: float,
        persistence: float,
        confidence: float,
        source_event_ids: list[str] | None = None,
        source_observation_ids: list[str] | None = None,
    ) -> StateChangeAssessment:
        """
        Create an integrated StateChangeAssessment from an
        already-computed StateDiff.
        """

        materiality = self.materiality_engine.assess(
            magnitude=magnitude,
            structural_relevance=structural_relevance,
            persistence=persistence,
            confidence=confidence,
        )

        return StateChangeAssessment(
            id=change_id,
            assessed_at=assessed_at,
            state_diff=diff,
            materiality=materiality,
            affected_paths=[
                change.path
                for change in diff.changes
            ],
            source_event_ids=source_event_ids or [],
            source_observation_ids=(
                source_observation_ids or []
            ),
        )