from __future__ import annotations

from datetime import datetime
from typing import Any

from .sequence import StateSpaceTransitionSequence
from .transition import (
    StateSpaceTransition,
    StateSpaceTransitionType,
)


class StateSpaceSequenceEngine:
    """
    Construct descriptive sequences from observed state-space
    transitions.

    The engine operates only on observed transitions. It does not
    forecast future states, infer causality, or determine whether
    an observed sequence will continue.
    """

    def build(
        self,
        *,
        sequence_id: str,
        transitions: list[StateSpaceTransition],
        metadata: dict[str, Any] | None = None,
    ) -> StateSpaceTransitionSequence:
        """
        Build a sequence from observed transitions.

        Transitions are ordered deterministically by assessed_at and
        then by transition ID.
        """
        ordered = sorted(
            transitions,
            key=lambda transition: (
                transition.assessed_at,
                transition.id,
            ),
        )

        if not ordered:
            raise ValueError(
                "At least one transition is required"
            )

        transition_ids = [
            transition.id
            for transition in ordered
        ]

        transition_types = [
            transition.transition_type
            for transition in ordered
        ]

        changed_dimensions = sorted(
            {
                dimension
                for transition in ordered
                for dimension
                in transition.changed_dimensions
            }
        )

        cumulative_magnitude = sum(
            transition.magnitude
            for transition in ordered
        )

        average_confidence = (
            sum(
                transition.confidence
                for transition in ordered
            )
            / len(ordered)
        )

        has_structural_shift = any(
            transition.transition_type
            == StateSpaceTransitionType.STRUCTURAL_SHIFT
            for transition in ordered
        )

        rationale = self._build_rationale(
            ordered
        )

        return StateSpaceTransitionSequence(
            id=sequence_id,
            start_time=ordered[0].assessed_at,
            end_time=ordered[-1].assessed_at,
            transition_ids=transition_ids,
            transition_types=transition_types,
            changed_dimensions=changed_dimensions,
            start_position_id=(
                ordered[0].previous_position_id
            ),
            end_position_id=(
                ordered[-1].current_position_id
            ),
            transition_count=len(ordered),
            cumulative_magnitude=(
                cumulative_magnitude
            ),
            average_confidence=(
                average_confidence
            ),
            has_structural_shift=(
                has_structural_shift
            ),
            rationale=rationale,
            metadata=dict(metadata or {}),
        )

    @staticmethod
    def _build_rationale(
        transitions: list[StateSpaceTransition],
    ) -> list[str]:
        """
        Build deterministic descriptive rationale for the
        observed sequence.
        """
        rationale: list[str] = []

        type_names = [
            transition.transition_type.value
            for transition in transitions
        ]

        rationale.append(
            "Observed transition sequence: "
            + " -> ".join(type_names)
            + "."
        )

        dimensions = sorted(
            {
                dimension
                for transition in transitions
                for dimension
                in transition.changed_dimensions
            }
        )

        if dimensions:
            rationale.append(
                "Affected dimensions: "
                + ", ".join(dimensions)
                + "."
            )

        if any(
            transition.transition_type
            == StateSpaceTransitionType.STRUCTURAL_SHIFT
            for transition in transitions
        ):
            rationale.append(
                "The observed sequence includes a "
                "structural shift."
            )

        return rationale