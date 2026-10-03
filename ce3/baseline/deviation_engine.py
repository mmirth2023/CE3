from __future__ import annotations

from datetime import datetime
from typing import Any

from .deviation import BaselineDeviation, DeviationDirection
from .models import BaselineReference


class DeviationEngine:
    """
    Compares an observed state against an established baseline.

    The engine describes observable deviation only.

    It does not determine causality, materiality, propagation,
    regime transition, economic consequences, or future outcomes.
    """

    def build(
        self,
        *,
        deviation_id: str,
        baseline: BaselineReference,
        observed_at: datetime,
        observed_state: dict[str, Any],
        affected_paths: list[str] | None = None,
        persistence: float = 0.0,
        confidence: float = 1.0,
        rationale: str = "",
        source_event_ids: list[str] | None = None,
        source_observation_ids: list[str] | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> BaselineDeviation:
        """
        Build a deviation assessment from a baseline and observed state.
        """
        direction, magnitude = self._compare_states(
            baseline.reference_state,
            observed_state,
        )

        return BaselineDeviation(
            id=deviation_id,
            baseline_id=baseline.id,
            system_id=baseline.system_id,
            dimension=baseline.dimension,
            observed_at=observed_at,
            baseline_state=baseline.reference_state,
            observed_state=observed_state,
            affected_paths=affected_paths or [],
            direction=direction,
            magnitude=magnitude,
            persistence=persistence,
            confidence=confidence,
            rationale=rationale,
            source_event_ids=source_event_ids or [],
            source_observation_ids=source_observation_ids or [],
            metadata=metadata or {},
        )

    def _compare_states(
        self,
        baseline_state: dict[str, Any],
        observed_state: dict[str, Any],
    ) -> tuple[DeviationDirection, float]:
        """
        Compare numeric values shared by baseline and observed state.

        The magnitude is the average absolute relative deviation
        across comparable numeric fields.

        Non-numeric fields are preserved in the deviation object but
        are not included in numeric magnitude calculation.
        """
        comparisons: list[tuple[float, float]] = []

        self._collect_numeric_comparisons(
            baseline_state,
            observed_state,
            comparisons,
        )

        if not comparisons:
            return DeviationDirection.NONE, 0.0

        relative_changes = [
            abs(observed - baseline) / abs(baseline)
            for baseline, observed in comparisons
            if baseline != 0
        ]

        if not relative_changes:
            magnitude = 0.0
        else:
            magnitude = sum(relative_changes) / len(relative_changes)

        directions: list[int] = []

        for baseline, observed in comparisons:
            if observed > baseline:
                directions.append(1)
            elif observed < baseline:
                directions.append(-1)

        if not directions or all(value == 0 for value in directions):
            direction = DeviationDirection.NONE
        elif all(value > 0 for value in directions):
            direction = DeviationDirection.ABOVE
        elif all(value < 0 for value in directions):
            direction = DeviationDirection.BELOW
        else:
            direction = DeviationDirection.MIXED

        return direction, magnitude

    def _collect_numeric_comparisons(
        self,
        baseline: dict[str, Any],
        observed: dict[str, Any],
        comparisons: list[tuple[float, float]],
    ) -> None:
        """
        Recursively collect numeric values present in both states.
        """
        for key, baseline_value in baseline.items():
            if key not in observed:
                continue

            observed_value = observed[key]

            if isinstance(baseline_value, dict) and isinstance(
                observed_value,
                dict,
            ):
                self._collect_numeric_comparisons(
                    baseline_value,
                    observed_value,
                    comparisons,
                )
                continue

            if isinstance(baseline_value, bool) or isinstance(
                observed_value,
                bool,
            ):
                continue

            if isinstance(baseline_value, (int, float)) and isinstance(
                observed_value,
                (int, float),
            ):
                comparisons.append(
                    (
                        float(baseline_value),
                        float(observed_value),
                    )
                )