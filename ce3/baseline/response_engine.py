from __future__ import annotations

from datetime import datetime
from typing import Any

from .response import ResponseDirection, SystemResponse


class ResponseEngine:
    """
    Compares observed system states and constructs a descriptive
    system response.

    The engine describes what changed between two observations.

    It does not determine causality, propagation, regime transition,
    economic consequences, or future outcomes.
    """

    def build(
        self,
        *,
        response_id: str,
        system_id: str,
        dimension: str,
        deviation_id: str,
        observed_at: datetime,
        state_before: dict[str, Any],
        state_after: dict[str, Any],
        affected_paths: list[str] | None = None,
        previous_observed_at: datetime | None = None,
        persistence: float = 0.0,
        confidence: float = 1.0,
        rationale: str = "",
        source_event_ids: list[str] | None = None,
        source_observation_ids: list[str] | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> SystemResponse:
        """
        Build a system response from two observed states.
        """
        direction, magnitude = self._compare_states(
            state_before,
            state_after,
        )

        latency_seconds = self._calculate_latency(
            previous_observed_at,
            observed_at,
        )

        return SystemResponse(
            id=response_id,
            system_id=system_id,
            dimension=dimension,
            deviation_id=deviation_id,
            observed_at=observed_at,
            response_state_before=state_before,
            response_state_after=state_after,
            affected_paths=affected_paths or [],
            direction=direction,
            magnitude=magnitude,
            latency_seconds=latency_seconds,
            persistence=persistence,
            confidence=confidence,
            rationale=rationale,
            source_event_ids=source_event_ids or [],
            source_observation_ids=source_observation_ids or [],
            metadata=metadata or {},
        )

    def _calculate_latency(
        self,
        previous_observed_at: datetime | None,
        observed_at: datetime,
    ) -> float:
        """
        Calculate elapsed time between observations.

        If no previous observation timestamp is supplied, latency
        defaults to zero.
        """
        if previous_observed_at is None:
            return 0.0

        latency = (
            observed_at - previous_observed_at
        ).total_seconds()

        if latency < 0:
            raise ValueError(
                "observed_at must be on or after previous_observed_at"
            )

        return latency

    def _compare_states(
        self,
        state_before: dict[str, Any],
        state_after: dict[str, Any],
    ) -> tuple[ResponseDirection, float]:
        """
        Compare numeric values shared by both states.

        Magnitude is the average absolute relative change across
        comparable numeric fields with non-zero prior values.

        Non-numeric fields are preserved in the response but do not
        contribute to numeric magnitude.
        """
        comparisons: list[tuple[float, float]] = []

        self._collect_numeric_comparisons(
            state_before,
            state_after,
            comparisons,
        )

        if not comparisons:
            return ResponseDirection.NONE, 0.0

        relative_changes = [
            abs(after - before) / abs(before)
            for before, after in comparisons
            if before != 0
        ]

        if not relative_changes:
            magnitude = 0.0
        else:
            magnitude = (
                sum(relative_changes)
                / len(relative_changes)
            )

        directions: list[int] = []

        for before, after in comparisons:
            if after > before:
                directions.append(1)
            elif after < before:
                directions.append(-1)

        if not directions:
            direction = ResponseDirection.NONE
        elif all(value > 0 for value in directions):
            direction = ResponseDirection.INCREASE
        elif all(value < 0 for value in directions):
            direction = ResponseDirection.DECREASE
        else:
            direction = ResponseDirection.MIXED

        return direction, magnitude

    def _collect_numeric_comparisons(
        self,
        before: dict[str, Any],
        after: dict[str, Any],
        comparisons: list[tuple[float, float]],
    ) -> None:
        """
        Recursively collect numeric values present in both states.
        """
        for key, before_value in before.items():
            if key not in after:
                continue

            after_value = after[key]

            if isinstance(before_value, dict) and isinstance(
                after_value,
                dict,
            ):
                self._collect_numeric_comparisons(
                    before_value,
                    after_value,
                    comparisons,
                )
                continue

            if isinstance(before_value, bool) or isinstance(
                after_value,
                bool,
            ):
                continue

            if isinstance(before_value, (int, float)) and isinstance(
                after_value,
                (int, float),
            ):
                comparisons.append(
                    (
                        float(before_value),
                        float(after_value),
                    )
                )