from __future__ import annotations

from collections import Counter
from typing import Any

from .sequence import StateSpaceTransitionSequence
from .sequence_analysis import (
    StateSpaceSequenceAnalysis,
    StateSpaceSequenceClassification,
)
from .transition import StateSpaceTransitionType


class StateSpaceSequenceAnalysisEngine:
    """
    Analyze an observed state-space transition sequence.

    The engine is descriptive. It identifies observable structure
    within an already observed sequence. It does not forecast future
    states, infer causality, estimate probabilities, or determine
    what happens next.
    """

    def analyze(
        self,
        *,
        analysis_id: str,
        sequence: StateSpaceTransitionSequence,
        metadata: dict[str, Any] | None = None,
    ) -> StateSpaceSequenceAnalysis:
        """
        Analyze an observed transition sequence.
        """
        transition_counts = Counter(
            sequence.transition_types
        )

        deterioration_count = transition_counts.get(
            StateSpaceTransitionType.DETERIORATION,
            0,
        )

        recovery_count = transition_counts.get(
            StateSpaceTransitionType.RECOVERY,
            0,
        )

        normalization_count = transition_counts.get(
            StateSpaceTransitionType.NORMALIZATION,
            0,
        )

        dimensional_shift_count = transition_counts.get(
            StateSpaceTransitionType.DIMENSIONAL_SHIFT,
            0,
        )

        structural_shift_count = transition_counts.get(
            StateSpaceTransitionType.STRUCTURAL_SHIFT,
            0,
        )

        none_count = transition_counts.get(
            StateSpaceTransitionType.NONE,
            0,
        )

        unknown_count = transition_counts.get(
            StateSpaceTransitionType.UNKNOWN,
            0,
        )

        dimension_counts = self._dimension_counts(
            sequence
        )

        repeated_dimensions = sorted(
            dimension
            for dimension, count
            in dimension_counts.items()
            if count > 1
        )

        dominant_transition_type = (
            self._dominant_transition_type(
                transition_counts
            )
        )

        dominant_dimension = (
            self._dominant_dimension(
                dimension_counts
            )
        )

        reversal_detected = self._detect_reversal(
            sequence
        )

        structural_shift_detected = (
            sequence.has_structural_shift
            or structural_shift_count > 0
        )

        classification = self._classify(
            sequence=sequence,
            deterioration_count=deterioration_count,
            recovery_count=recovery_count,
            normalization_count=normalization_count,
            dimensional_shift_count=dimensional_shift_count,
            structural_shift_count=structural_shift_count,
            none_count=none_count,
            unknown_count=unknown_count,
            reversal_detected=reversal_detected,
        )

        transition_density = (
            self._transition_density(sequence)
        )

        rationale = self._build_rationale(
            classification=classification,
            deterioration_count=deterioration_count,
            recovery_count=recovery_count,
            normalization_count=normalization_count,
            dimensional_shift_count=dimensional_shift_count,
            structural_shift_count=structural_shift_count,
            reversal_detected=reversal_detected,
            dominant_transition_type=(
                dominant_transition_type
            ),
            dominant_dimension=dominant_dimension,
        )

        return StateSpaceSequenceAnalysis(
            id=analysis_id,
            sequence_id=sequence.id,
            classification=classification,
            transition_count=sequence.transition_count,
            deterioration_count=deterioration_count,
            recovery_count=recovery_count,
            normalization_count=normalization_count,
            dimensional_shift_count=(
                dimensional_shift_count
            ),
            structural_shift_count=(
                structural_shift_count
            ),
            none_count=none_count,
            unknown_count=unknown_count,
            changed_dimensions=list(
                sequence.changed_dimensions
            ),
            repeated_dimensions=repeated_dimensions,
            reversal_detected=reversal_detected,
            structural_shift_detected=(
                structural_shift_detected
            ),
            dominant_transition_type=(
                dominant_transition_type
            ),
            dominant_dimension=dominant_dimension,
            transition_density=transition_density,
            cumulative_magnitude=(
                sequence.cumulative_magnitude
            ),
            average_confidence=(
                sequence.average_confidence
            ),
            rationale=rationale,
            metadata=dict(metadata or {}),
        )

    @staticmethod
    def _dimension_counts(
        sequence: StateSpaceTransitionSequence,
    ) -> Counter[str]:
        """
        Count how many observed transitions affected each
        dimension.
        """
        counts: Counter[str] = Counter()

        for dimensions in sequence.transition_dimensions:
            counts.update(dimensions)

        return counts

    @staticmethod
    def _dominant_transition_type(
        transition_counts: Counter,
    ) -> str | None:
        """
        Return the most frequently observed transition type.

        Ties are resolved deterministically using enum value order.
        """
        if not transition_counts:
            return None

        ranked = sorted(
            transition_counts.items(),
            key=lambda item: (
                -item[1],
                item[0].value,
            ),
        )

        return ranked[0][0].value

    @staticmethod
    def _dominant_dimension(
        dimension_counts: Counter[str],
    ) -> str | None:
        """
        Return the most frequently affected dimension.

        Ties are resolved deterministically using dimension name
        order.
        """
        if not dimension_counts:
            return None

        ranked = sorted(
            dimension_counts.items(),
            key=lambda item: (
                -item[1],
                item[0],
            ),
        )

        return ranked[0][0]

    @staticmethod
    def _detect_reversal(
        sequence: StateSpaceTransitionSequence,
    ) -> bool:
        """
        Detect a deterioration-to-recovery or recovery-to-
        deterioration reversal in the observed transition order.
        """
        directional_types = [
            transition_type
            for transition_type
            in sequence.transition_types
            if transition_type
            in {
                StateSpaceTransitionType.DETERIORATION,
                StateSpaceTransitionType.RECOVERY,
            }
        ]

        if len(directional_types) < 2:
            return False

        for previous, current in zip(
            directional_types,
            directional_types[1:],
        ):
            if previous != current:
                return True

        return False

    @staticmethod
    def _classify(
        *,
        sequence: StateSpaceTransitionSequence,
        deterioration_count: int,
        recovery_count: int,
        normalization_count: int,
        dimensional_shift_count: int,
        structural_shift_count: int,
        none_count: int,
        unknown_count: int,
        reversal_detected: bool,
    ) -> StateSpaceSequenceClassification:
        """
        Classify the observed trajectory structure.
        """
        if sequence.transition_count == 0:
            return StateSpaceSequenceClassification.EMPTY

        if structural_shift_count > 0:
            if reversal_detected:
                return StateSpaceSequenceClassification.REVERSAL

            return StateSpaceSequenceClassification.STRUCTURAL

        if reversal_detected:
            return StateSpaceSequenceClassification.REVERSAL

        if (
            deterioration_count > 0
            and recovery_count == 0
            and normalization_count == 0
            and dimensional_shift_count == 0
        ):
            return StateSpaceSequenceClassification.DETERIORATING

        if (
            recovery_count > 0
            and deterioration_count == 0
            and normalization_count == 0
            and dimensional_shift_count == 0
        ):
            return StateSpaceSequenceClassification.RECOVERING

        if (
            normalization_count > 0
            and deterioration_count == 0
            and recovery_count == 0
            and dimensional_shift_count == 0
        ):
            return StateSpaceSequenceClassification.STABLE

        if (
            deterioration_count > 0
            and recovery_count > 0
        ):
            return StateSpaceSequenceClassification.MIXED

        if (
            dimensional_shift_count > 0
            or unknown_count > 0
        ):
            return StateSpaceSequenceClassification.COMPLEX

        if (
            none_count == sequence.transition_count
        ):
            return StateSpaceSequenceClassification.STABLE

        return StateSpaceSequenceClassification.UNKNOWN

    @staticmethod
    def _transition_density(
        sequence: StateSpaceTransitionSequence,
    ) -> float:
        """
        Calculate observed transition density.

        Density is expressed as transitions per hour across the
        observed sequence window. A single transition has zero
        elapsed duration and therefore produces zero density.
        """
        duration_seconds = (
            sequence.end_time
            - sequence.start_time
        ).total_seconds()

        if duration_seconds <= 0:
            return 0.0

        duration_hours = duration_seconds / 3600.0

        return (
            sequence.transition_count
            / duration_hours
        )

    @staticmethod
    def _build_rationale(
        *,
        classification: StateSpaceSequenceClassification,
        deterioration_count: int,
        recovery_count: int,
        normalization_count: int,
        dimensional_shift_count: int,
        structural_shift_count: int,
        reversal_detected: bool,
        dominant_transition_type: str | None,
        dominant_dimension: str | None,
    ) -> list[str]:
        """
        Build deterministic descriptive rationale.
        """
        rationale: list[str] = []

        rationale.append(
            "Observed sequence classified as "
            f"{classification.value}."
        )

        if deterioration_count:
            rationale.append(
                "Observed deterioration transitions: "
                f"{deterioration_count}."
            )

        if recovery_count:
            rationale.append(
                "Observed recovery transitions: "
                f"{recovery_count}."
            )

        if normalization_count:
            rationale.append(
                "Observed normalization transitions: "
                f"{normalization_count}."
            )

        if dimensional_shift_count:
            rationale.append(
                "Observed dimensional shifts: "
                f"{dimensional_shift_count}."
            )

        if structural_shift_count:
            rationale.append(
                "Observed structural shifts: "
                f"{structural_shift_count}."
            )

        if reversal_detected:
            rationale.append(
                "The observed sequence contains a "
                "directional reversal."
            )

        if dominant_transition_type is not None:
            rationale.append(
                "Dominant transition type: "
                f"{dominant_transition_type}."
            )

        if dominant_dimension is not None:
            rationale.append(
                "Dominant affected dimension: "
                f"{dominant_dimension}."
            )

        return rationale