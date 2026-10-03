from __future__ import annotations

from typing import Any

from .deviation import BaselineDeviation
from .response import SystemResponse
from .response_analysis import (
    ResponseAnalysis,
    ResponseClassification,
)


class ResponseAnalysisEngine:
    """
    Analyzes an observed system response relative to a baseline deviation.

    The engine describes whether the observed response moved toward,
    away from, or remained near the established baseline.

    It does not determine causality, propagation, regime transition,
    economic consequences, or future outcomes.
    """

    def build(
        self,
        *,
        analysis_id: str,
        deviation: BaselineDeviation,
        response: SystemResponse,
        baseline_state: dict[str, Any] | None = None,
        confidence: float | None = None,
        rationale: str = "",
        metadata: dict[str, Any] | None = None,
    ) -> ResponseAnalysis:
        """
        Build a descriptive response analysis.
        """
        if baseline_state is None:
            distance_before = deviation.magnitude
            distance_after = self._estimate_distance_after(
                deviation,
                response,
            )
        else:
            distance_before = self._state_distance(
                baseline_state,
                response.response_state_before,
            )
            distance_after = self._state_distance(
                baseline_state,
                response.response_state_after,
            )

        classification = self._classify(
            distance_before,
            distance_after,
            response,
        )

        response_strength = self._response_strength(
            distance_before,
            distance_after,
        )

        analysis_confidence = (
            response.confidence
            if confidence is None
            else confidence
        )

        return ResponseAnalysis(
            id=analysis_id,
            deviation_id=deviation.id,
            response_id=response.id,
            system_id=response.system_id,
            dimension=response.dimension,
            classification=classification,
            baseline_distance_before=distance_before,
            baseline_distance_after=distance_after,
            response_strength=response_strength,
            persistence=response.persistence,
            confidence=analysis_confidence,
            rationale=rationale,
            affected_paths=response.affected_paths,
            source_event_ids=response.source_event_ids,
            source_observation_ids=response.source_observation_ids,
            metadata=metadata or {},
        )

    def _estimate_distance_after(
        self,
        deviation: BaselineDeviation,
        response: SystemResponse,
    ) -> float:
        """
        Estimate post-response baseline distance when the caller
        does not provide the baseline state.
        """
        if deviation.direction.value == "none":
            return response.magnitude

        if response.direction.value == "none":
            return deviation.magnitude

        if deviation.direction.value == "mixed":
            return deviation.magnitude

        deviation_direction = (
            1
            if deviation.direction.value == "above"
            else -1
        )

        response_direction = (
            1
            if response.direction.value == "increase"
            else -1
        )

        if deviation_direction == response_direction:
            return deviation.magnitude + response.magnitude

        return max(
            0.0,
            deviation.magnitude - response.magnitude,
        )

    def _state_distance(
        self,
        baseline: dict[str, Any],
        observed: dict[str, Any],
    ) -> float:
        """
        Calculate average absolute relative distance from baseline
        across comparable numeric fields.
        """
        distances: list[float] = []

        self._collect_distances(
            baseline,
            observed,
            distances,
        )

        if not distances:
            return 0.0

        return sum(distances) / len(distances)

    def _collect_distances(
        self,
        baseline: dict[str, Any],
        observed: dict[str, Any],
        distances: list[float],
    ) -> None:
        """
        Recursively collect relative distances from baseline.
        """
        for key, baseline_value in baseline.items():
            if key not in observed:
                continue

            observed_value = observed[key]

            if isinstance(baseline_value, dict) and isinstance(
                observed_value,
                dict,
            ):
                self._collect_distances(
                    baseline_value,
                    observed_value,
                    distances,
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
                if baseline_value == 0:
                    continue

                distances.append(
                    abs(
                        float(observed_value)
                        - float(baseline_value)
                    )
                    / abs(float(baseline_value))
                )

    def _response_strength(
        self,
        distance_before: float,
        distance_after: float,
    ) -> float:
        """
        Calculate the absolute change in baseline distance.
        """
        return abs(
            distance_before - distance_after
        )

    def _classify(
        self,
        distance_before: float,
        distance_after: float,
        response: SystemResponse,
    ) -> ResponseClassification:
        """
        Classify the observed response from baseline-distance movement.
        """
        tolerance = 1e-12

        if (
            distance_before <= tolerance
            and distance_after <= tolerance
        ):
            return ResponseClassification.STABLE

        if distance_after < distance_before - tolerance:
            if distance_after <= tolerance:
                return ResponseClassification.NORMALIZED

            return ResponseClassification.NORMALIZED

        if distance_after > distance_before + tolerance:
            return ResponseClassification.AMPLIFIED

        if response.persistence > 0.5:
            return ResponseClassification.PERSISTENT

        if response.direction.value == "none":
            return ResponseClassification.STABLE

        return ResponseClassification.STABLE